from collections.abc import Iterator

from nicegui import ui


class input_view(ui.element):  # noqa: N801 this is the nicegui convention
    """The component which will display the user's input.

    Usage:
        First, in the page handler, create the view -- do NOT put this in a refreshable
        method, as the constructor adds CSS and will duplicate stuff. The `full_text` argument is
        the **original** text, the thing that the user needs to type -- the user's input starts empty.

        Then, whenever your text updates, call `set_text` on the input view. This updates the
        **user input** of the input view. If you need to change the background text for whatever
        reason, use `set_original_text`.

    Example:
        ```python
        @ui.page("/input")
        def page():
            state = State()
            iv = input_view.input_view("The quick brown fox jumps over the lazy dog.")
            def on_key(key):
                state.text += key
                iv.set_text(state.text)
            input_method.on_key(on_key)
        ```

    """

    CSS = """
.input-view {
    padding: 8px;
    border-radius: 5px;
    background-color: var(--q-dark);
    font-family: monospace;
    color: var(--q-secondary);
    word-break: break-all;
    display: grid;
}

.input-view-bg {
    grid-area: 1 / 1 / 2 / 2;
}

.input-view-fg {
    grid-area: 1 / 1 / 2 / 2;
}

.input-view-fg div {
    display: inline;
}

.input-view-fg span.c, .input-view-fg div.c {
    background-color: var(--q-positive);
    color: var(--q-dark);
}

.input-view-fg span.w, .input-view-fg div.w {
    background-color: var(--q-negative);
}

.input-view-fg span.cursor, .input-view-fg div.cursor {
    color: white;
    display: inline-block;
}
"""

    def __init__(self, full_text: str) -> None:
        super().__init__("div")
        ui.add_css(self.CSS)

        self.classes("input-view")
        with self:
            self.full_text_label = ui.label(full_text).classes("input-view-bg")
            self.text_input = ui.element().classes("input-view-fg")
            with self.text_input:
                ui.label("_").classes("cursor")

        self.full_text = full_text
        self.value = ""

    def _parse_text(self, user_text: str) -> Iterator[tuple[str, bool]]:
        """Get a token list of string slices and whether they are correct."""
        if len(user_text) == 0:
            return iter(())

        mask = []
        for i in range(len(user_text)):
            if i < len(self.full_text):
                mask.append(user_text[i] == self.full_text[i])
            else:
                mask.append(False)

        index = 0
        cur_v = mask[0]

        while index < len(mask):
            next_change_at = index + 1
            while next_change_at < len(mask) and mask[next_change_at] == cur_v:
                next_change_at += 1
            yield (user_text[index:next_change_at], cur_v)
            index = next_change_at
            cur_v = not cur_v

    def set_original_text(self, value: str) -> None:
        """Reset the **background** text. You're probably looking for `set_text`.

        Example:
            ```python
        # `text` is what the user is supposed to type.
        def new_txt_selected_handler(text):
            iv.set_original_text(text)
            ...
            ```

        """
        self.full_text = value
        self.full_text_label.set_text(value)

    def set_text(self, value: str) -> None:
        """Set the current **user** input -- what should be displayed in the foreground.

        Additionally, it adds highlighting based on where the user types a correct character and
        where the user types an incorrect character.

        Example:
                ```python
        state = State()
        def on_key(key):
            state.text += key
            iv.set_text(state.text)  # here
            ...
        input_method.on_key(on_key)
                ```

        """
        self.text_input.clear()
        if value == "":
            return
        parsed = self._parse_text(value)
        with self.text_input:
            for tok, correct in parsed:
                ui.html(tok.replace(" ", "&nbsp;")).classes("c" if correct else "w")

            if len(value) < len(self.full_text):
                ui.label("_").classes("cursor")
