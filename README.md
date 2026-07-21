<p align="center">
  <img src="web_dist/muscriptor-logo-v2.png" alt="MuScriptor logo" width="300">
</p>

# ComfyUI-MuScriptor

[English](#english) | [Português](#português)

---

<a name="english"></a>
## English

**ComfyUI-MuScriptor** is a custom node extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that integrates [MuScriptor](https://github.com/muscriptor/muscriptor), a state-of-the-art multi-instrument music transcription model developed by [Kyutai](https://kyutai.org) and [Mirelo](https://www.mirelo.ai).

It transcribes multi-instrument audio (WAV, MP3, FLAC, etc.) into high-quality MIDI files directly inside your ComfyUI generation pipelines.

### 🌟 Key Features
- **Audio-to-MIDI Transcription**: Convert audio waveforms or audio files into multi-instrument MIDI.
- **ComfyUI Integration**: Connects seamlessly with ComfyUI's `AUDIO` output type or local audio files.
- **Model Sizes**: Supports `small` (103M), `medium` (307M, default), and `large` (1.4B) model variants.
- **Instrument Filtering**: Restrict transcription output to specific instrument groups (e.g. `acoustic_piano`, `violin`, `drums`).
- **JSON Notes Output**: Returns both the generated `.mid` file path and a structured JSON array of decoded note events.
- **In-Memory Caching**: Automatic model caching for instantaneous execution on subsequent workflow runs.

---

### 🚀 Installation

#### 1. Clone into ComfyUI custom_nodes
Navigate to your ComfyUI `custom_nodes` directory and clone this repository:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/ComfyUI-MuScriptor.git comfyui-muscriptor
```

#### 2. Install Requirements
Install dependencies in your ComfyUI environment:

```bash
pip install -r comfyui-muscriptor/requirements.txt
```

#### 3. HuggingFace Login (Required)
The model weights are hosted on [HuggingFace](https://huggingface.co/MuScriptor) and require accepting their license:

1. Accept the model license on the [muscriptor-medium HuggingFace page](https://huggingface.co/MuScriptor/muscriptor-medium).
2. Authenticate on your machine:
   ```bash
   export HF_TOKEN=hf_...
   ```
   Or run `hf auth login` in your terminal.

---

### 🎛️ ComfyUI Node Documentation

**Node Category**: `MuScriptor`  
**Node Name**: `MuScriptor Transcribe Audio to MIDI`

#### Inputs:
| Parameter | Type | Description |
|---|---|---|
| `audio` | `AUDIO` *(optional)* | ComfyUI standard `AUDIO` port. Takes priority if connected. |
| `audio_path` | `STRING` *(optional)* | Local file path to an audio file (WAV, MP3, FLAC, etc.). |
| `model_size` | `ENUM` | Model size: `small`, `medium` (default), or `large`. |
| `device` | `ENUM` | Device target: `auto`, `cuda`, `cpu`, or `mps`. |
| `dtype` | `ENUM` | Computation precision: `auto`, `float32`, `float16`, `bfloat16`. |
| `use_sampling` | `BOOLEAN` | Use temperature sampling instead of greedy decoding (default: `False`). |
| `temperature` | `FLOAT` | Sampling temperature (0.0 to 2.0). |
| `cfg_coef` | `FLOAT` | Classifier-free guidance coefficient (default: `1.0`). |
| `beam_size` | `INT` | Beam search width (`1` = greedy/sampling, `≥2` = beam search). |
| `prelude_forcing` | `BOOLEAN` | Teacher-force tie section across chunk boundaries for optimal quality (default: `True`). |
| `strict_eos` | `BOOLEAN` | Raise an error if a chunk fails to emit EOS within budget (default: `False`). |
| `filename_prefix` | `STRING` | Output MIDI filename prefix (default: `muscriptor_transcription`). |
| `instruments` | `STRING` | Optional comma-separated or multiline list of allowed instrument names. |

#### Outputs:
| Output | Type | Description |
|---|---|---|
| `midi_path` | `STRING` | Absolute file path to the saved `.mid` file in ComfyUI's `output` directory. |
| `notes_json` | `STRING` | JSON string containing an array of all decoded note events (pitch, start_time, end_time, instrument). |

---
---

<a name="português"></a>
## Português

**ComfyUI-MuScriptor** é uma extensão de nó customizado para o [ComfyUI](https://github.comfyanonymous/ComfyUI) que integra o [MuScriptor](https://github.com/muscriptor/muscriptor), um modelo de transcrição musical de última geração desenvolvido por [Kyutai](https://kyutai.org) e [Mirelo](https://www.mirelo.ai).

Ele transcreve áudio de múltiplos instrumentos (WAV, MP3, FLAC, etc.) diretamente em arquivos MIDI de alta qualidade dentro dos seus fluxos de trabalho (workflows) no ComfyUI.

### 🌟 Funcionalidades Principais
- **Transcrição de Áudio para MIDI**: Converta sinais de áudio ou arquivos locais em arquivos MIDI multi-instrumentos.
- **Integração Total com ComfyUI**: Funciona com saídas do tipo `AUDIO` do ComfyUI ou com caminhos de arquivos locais.
- **Variantes de Modelo**: Suporta os modelos `small` (103M), `medium` (307M, padrão) e `large` (1.4B).
- **Filtro de Instrumentos**: Restrinja a transcrição a instrumentos específicos (ex: `acoustic_piano`, `violin`, `drums`).
- **Saída de Notas em JSON**: Retorna tanto o caminho do arquivo `.mid` salvo quanto uma lista estruturada de notas em formato JSON.
- **Cache em Memória**: Carregamento automático do modelo em RAM/VRAM para execuções instantâneas em execuções subsequentes.

---

### 🚀 Instalação

#### 1. Clonar na pasta custom_nodes
Navegue até a pasta `custom_nodes` da sua instalação do ComfyUI e clone este repositório:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/seu-usuario/ComfyUI-MuScriptor.git comfyui-muscriptor
```

#### 2. Instalar Requisitos
Instale as dependências no seu ambiente Python do ComfyUI:

```bash
pip install -r comfyui-muscriptor/requirements.txt
```

#### 3. Autenticação HuggingFace (Obrigatório)
Os pesos dos modelos estão hospedados no [HuggingFace](https://huggingface.co/MuScriptor) e exigem aceitar os termos de uso:

1. Aceite a licença do modelo na [página do muscriptor-medium no HuggingFace](https://huggingface.co/MuScriptor/muscriptor-medium).
2. Autentique no seu sistema:
   ```bash
   export HF_TOKEN=hf_...
   ```
   Ou execute `hf auth login` no terminal.

---

### 🎛️ Documentação do Nó no ComfyUI

**Categoria do Nó**: `MuScriptor`  
**Nome do Nó**: `MuScriptor Transcribe Audio to MIDI`

#### Entradas (Inputs):
| Parâmetro | Tipo | Descrição |
|---|---|---|
| `audio` | `AUDIO` *(opcional)* | Porta padrão de áudio do ComfyUI. Tem prioridade se conectada. |
| `audio_path` | `STRING` *(opcional)* | Caminho local para um arquivo de áudio (WAV, MP3, FLAC, etc.). |
| `model_size` | `ENUM` | Tamanho do modelo: `small`, `medium` (padrão) ou `large`. |
| `device` | `ENUM` | Dispositivo de execução: `auto`, `cuda`, `cpu` ou `mps`. |
| `dtype` | `ENUM` | Precisão numérica: `auto`, `float32`, `float16`, `bfloat16`. |
| `use_sampling` | `BOOLEAN` | Usar amostragem por temperatura em vez de decodificação gulosa (padrão: `False`). |
| `temperature` | `FLOAT` | Temperatura da amostragem (0.0 a 2.0). |
| `cfg_coef` | `FLOAT` | Coeficiente do Classifier-Free Guidance (padrão: `1.0`). |
| `beam_size` | `INT` | Largura da busca por feixe (Beam Search) (`1` = guloso, `≥2` = busca por feixe). |
| `prelude_forcing` | `BOOLEAN` | Forçamento do prólogo de ligação entre blocos para qualidade máxima (padrão: `True`). |
| `strict_eos` | `BOOLEAN` | Emitir erro caso um bloco não emita EOS no orçamento (padrão: `False`). |
| `filename_prefix` | `STRING` | Prefixo do arquivo MIDI de saída (padrão: `muscriptor_transcription`). |
| `instruments` | `STRING` | Lista opcional de nomes de instrumentos permitidos (separados por vírgula ou linha). |

#### Saídas (Outputs):
| Saída | Tipo | Descrição |
|---|---|---|
| `midi_path` | `STRING` | Caminho absoluto para o arquivo `.mid` salvo na pasta `output` do ComfyUI. |
| `notes_json` | `STRING` | String JSON contendo um array com todas as notas decodificadas (pitch, start_time, end_time, instrument). |

---

## License
MIT License
