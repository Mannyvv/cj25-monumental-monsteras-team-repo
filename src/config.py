from typing import TypedDict

from audio_style_input import AudioEditorComponent
from gridDrawing import CanvasDrawing
from input_method_proto import IInputMethod
from rpg_text_input import Keyboard

PROJECT_NAME: str = "Dynamic Typing"
PROJECT_DESCRIPTION: str = "How fast can you type?"


class InputMethodSpec(TypedDict):
    """Specifications for an input method to be added to the main page."""

    name: str
    path: str
    icon: str
    component: type[IInputMethod] | None


# INPUT METHODS
INPUT_METHODS: list[InputMethodSpec] = [
    {
        "name": "Record Player",
        "path": "audio-input",
        "icon": "",
        "component": AudioEditorComponent,
    },
    {
        "name": "WASD",
        "path": "wasd",
        "icon": "",
        "component": Keyboard,
    },
    {
        "name": "Canvas Drawing",
        "path": "canvas-drawing",
        "icon": "",
        "component": CanvasDrawing,
    },
    {
        "name": "Color Picker",
        "path": "color-picker",
        "icon": "",
        "component": None,
    },
    {
        "name": "Circle Selector",
        "path": "circle-selector",
        "icon": "",
        "component": None,
    },
]

# COLORS
COLOR_STYLE: dict[str, str] = {
    "primary": "#12E7B2",
    "secondary": "#7D53DE",
    "primary_bg": "#111111",
    "secondary_bg": "#1B1B1B",
    "contrast": "#F9F9F9",
}
