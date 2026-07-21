"""ComfyUI custom node loader for MuScriptor."""

import sys

# Register this module directory as the 'muscriptor' package in sys.modules
# so that all internal absolute imports (e.g. from muscriptor.events import ...) resolve properly.
sys.modules['muscriptor'] = sys.modules[__name__]

from .comfy_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
