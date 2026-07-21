import os
import re
import sys
import time
import json
import torch

from muscriptor.transcription_model import TranscriptionModel
from muscriptor.events import NoteStartEvent, NoteEndEvent, ProgressEvent
from muscriptor.tokenizer.mt3 import resolve_instrument_names

# Cache dictionary to keep loaded model instances in memory
_MODEL_CACHE = {}

def get_model(model_size: str, device: str, dtype: str) -> TranscriptionModel:
    """Helper to load and cache the transcription model."""
    import muscriptor.accelerator
    
    # Resolve torch device
    if device == "auto":
        model_device = (
            muscriptor.accelerator.current_accelerator()
            if muscriptor.accelerator.is_available()
            else torch.device("cpu")
        )
    else:
        model_device = torch.device(device)
        
    # Resolve dtype
    if dtype == "auto":
        model_dtype = torch.float16 if model_device.type == "mps" else torch.float32
    else:
        model_dtype = getattr(torch, dtype)

    cache_key = (model_size, str(model_device), str(model_dtype))
    
    if cache_key not in _MODEL_CACHE:
        # Clear other cached models to avoid CUDA OOM / memory bloat
        _MODEL_CACHE.clear()
        
        print(f"[MuScriptor] Loading model (size={model_size}, device={model_device}, dtype={model_dtype})...")
        model = TranscriptionModel.load_model(
            weights_path=model_size,
            device=model_device,
            dtype=model_dtype
        )
        _MODEL_CACHE[cache_key] = model
        
    return _MODEL_CACHE[cache_key]


def events_to_notes_list(events) -> list[dict]:
    """Extract and reconstruct list of notes from transcription events."""
    notes = []
    open_notes = {}
    for ev in events:
        if isinstance(ev, NoteStartEvent):
            note = {
                "pitch": ev.pitch,
                "start_time": round(ev.start_time, 4),
                "end_time": round(ev.start_time, 4),
                "instrument": ev.instrument,
            }
            open_notes[ev.index] = note
        elif isinstance(ev, NoteEndEvent):
            if ev.start_event_index in open_notes:
                note = open_notes.pop(ev.start_event_index)
                note["end_time"] = round(ev.end_time, 4)
                notes.append(note)
    
    # Sort notes primarily by start time, and then by pitch
    notes.sort(key=lambda x: (x["start_time"], x["pitch"]))
    return notes


class MuScriptorTranscribe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_size": (["small", "medium", "large"], {"default": "medium"}),
                "device": (["auto", "cpu", "cuda", "mps"], {"default": "auto"}),
                "dtype": (["auto", "float32", "float16", "bfloat16"], {"default": "auto"}),
                "use_sampling": ("BOOLEAN", {"default": False}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
                "cfg_coef": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "beam_size": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "prelude_forcing": ("BOOLEAN", {"default": True}),
                "strict_eos": ("BOOLEAN", {"default": False}),
                "filename_prefix": ("STRING", {"default": "muscriptor_transcription"}),
            },
            "optional": {
                "audio": ("AUDIO",),
                "audio_path": ("STRING", {"default": ""}),
                "instruments": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("midi_path", "notes_json")
    FUNCTION = "transcribe_audio"
    CATEGORY = "MuScriptor"

    def transcribe_audio(
        self,
        model_size,
        device,
        dtype,
        use_sampling,
        temperature,
        cfg_coef,
        beam_size,
        prelude_forcing,
        strict_eos,
        filename_prefix,
        audio=None,
        audio_path="",
        instruments=""
    ):
        # 1. Resolve Audio Input
        transcribe_input = None
        if audio is not None:
            # ComfyUI audio is a dict: {'waveform': torch.Tensor, 'sample_rate': int}
            waveform = audio.get("waveform")
            sample_rate = audio.get("sample_rate")
            if waveform is not None and sample_rate is not None:
                # ComfyUI waveform tensor is shape [batch, channels, samples]
                if waveform.ndim == 3:
                    waveform = waveform[0]  # Take first batch item: [channels, samples]
                transcribe_input = (waveform, sample_rate)
            
        if transcribe_input is None:
            if audio_path and audio_path.strip():
                clean_path = audio_path.strip()
                if os.path.exists(clean_path):
                    transcribe_input = clean_path
                else:
                    raise FileNotFoundError(f"[MuScriptor] The audio file path does not exist: {clean_path}")
            else:
                raise ValueError("[MuScriptor] You must provide either the 'audio' input link or a valid 'audio_path'.")

        # 2. Resolve Instruments constraint (optional)
        instrument_list = None
        if instruments and instruments.strip():
            tokens = [n.strip() for n in re.split(r'[,\n]', instruments) if n.strip()]
            if tokens:
                try:
                    instrument_list = resolve_instrument_names(tokens)
                    print(f"[MuScriptor] Constraining transcription to instruments: {', '.join(instrument_list)}")
                except ValueError as e:
                    raise ValueError(f"[MuScriptor] Error resolving instrument names: {e}")

        # 3. Load Model
        model = get_model(model_size, device, dtype)

        # 4. Perform Transcription
        print("[MuScriptor] Starting music transcription...")
        events_iterator = model.transcribe(
            audio=transcribe_input,
            use_sampling=use_sampling,
            temperature=temperature,
            cfg_coef=cfg_coef,
            instruments=instrument_list,
            batch_size=1,  # prelude_forcing=True requires batch_size=1
            no_eos_is_ok=not strict_eos,
            beam_size=beam_size,
            prelude_forcing=prelude_forcing,
        )

        # We consume the generator to construct events list
        events = []
        for ev in events_iterator:
            if isinstance(ev, ProgressEvent):
                # Print progress updates in console
                pct = (ev.completed / ev.total) * 100 if ev.total > 0 else 0
                print(f"[MuScriptor] Progress: {ev.completed}/{ev.total} chunks ({pct:.1f}%)")
            else:
                events.append(ev)

        # 5. Generate outputs
        midi_bytes = model.events_to_midi_bytes(events)
        notes_list = events_to_notes_list(events)
        notes_json = json.dumps(notes_list, indent=2)

        # 6. Save MIDI file to ComfyUI Output directory
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except ImportError:
            output_dir = os.path.join(os.getcwd(), "output")
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{filename_prefix}_{timestamp}.mid"
        midi_path = os.path.join(output_dir, filename)

        with open(midi_path, "wb") as f:
            f.write(midi_bytes)

        print(f"[MuScriptor] Transcription complete! Saved MIDI to: {midi_path}")
        return (midi_path, notes_json)


NODE_CLASS_MAPPINGS = {
    "MuScriptorTranscribe": MuScriptorTranscribe,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MuScriptorTranscribe": "MuScriptor Transcribe Audio to MIDI",
}
