import time
from dataclasses import dataclass

from nicegui import ui

import input_method_proto
import input_view
from config import INPUT_METHODS


def get_input_method_by_name(inmth: str) -> type[input_method_proto.IInputMethod] | None:
    """Get an input method class by it's name.

    :returns: `type[IInputMethod]` on success, `None` on failure.
    """
    for input_method in INPUT_METHODS:
        if inmth == input_method["path"]:
            return input_method["component"]
    return None


def create_header(method: str) -> ui.label:
    """Create header label."""
    with ui.header(elevated=True).classes("align-center justify-center"):
        return ui.label(f"test: {method}").classes("text-center text-lg")


def create_time_chips() -> tuple[ui.chip, ui.chip, ui.chip]:
    """Create chips for timer, wpm, and wph."""
    with ui.row().classes("w-full justify-center items-center gap-4"):
        timer_label = ui.chip("TIMER: 0:00", color="#6AC251", icon="timer")
        wpm_label = ui.chip("WPM: --", color="#e5e5e5", icon="watch")
        wph_label = ui.chip("WPH: --", color="#e5e5e5", icon="hourglass_top")

    return timer_label, wpm_label, wph_label


@dataclass
class TimerState:
    """Class for timer."""

    active: bool = False
    container: ui.timer | None = None
    start: float | None = None


def setup(
    method: str,
    text_to_use: str,
    state: str,
    chip_package: tuple[ui.chip, ui.chip, ui.chip],
    iv: input_view.input_view,
) -> None:
    """Set up the on_text_update and time associated."""
    input_method = get_input_method_by_name(method)()
    timer = TimerState()
    timer_label, wpm_label, wph_label = chip_package

    def on_text_update(txt: str) -> None:
        if not timer.active:
            timer.container = ui.timer(1, lambda: timer_label.set_text(iv.update_timer()))
            timer.active = True
            timer.start = time.time()

        iv.set_text(txt)
        state.text = txt

        if len(txt) == len(text_to_use):
            elapsed = time.time() - timer.start if timer.start else 0
            if elapsed > 0:
                wpm = (len(txt) / 5) / (elapsed / 60)
                wpm_label.set_text(f"Finished! WPM: {int(wpm)}")
                wph_label.set_text(f"Finished! WPH: {int(wpm * 60)}")
            stop_timer()

    def stop_timer() -> None:
        if timer.container:
            timer.container.deactivate()

    input_method.on_text_update(on_text_update)
    ui.on("disconnect", stop_timer)


@dataclass
class WpmTesterPageState:
    """The page state."""

    """Useless for now, may be useful later?"""
    text: str


async def wpm_tester_page(method: str) -> None:
    """Create the actual page which tests the wpm.

    Usage:
        In main.py, use @ui.page("/test/{method}")(this) then this takes
        the method from the url
    """
    state = WpmTesterPageState("")

    input_method_def = get_input_method_by_name(method)
    if input_method_def is None:
        ui.navigate.to("/")
        return

    # TODO: get og text from babbler module
    text_to_use = "the quick brown fox jumps over the lazy dog"
    iv = input_view.input_view(text_to_use).classes("w-full")

    create_header(method)
    timer_label, wpm_label, wph_label = create_time_chips()

    chip_package = timer_label, wpm_label, wph_label
    setup(method, text_to_use, state, chip_package, iv)
