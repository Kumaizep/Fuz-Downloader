import collections
from blessed import Terminal

term = Terminal()


class Theme:
    def __init__(self):
        self.Question = collections.namedtuple(
            "question", "mark_color brackets_color default_color"
        )
        self.Editor = collections.namedtuple("editor", "opening_prompt")
        self.Checkbox = collections.namedtuple(
            "common",
            "selection_color selection_icon selected_color unselected_color selected_icon unselected_icon",
        )
        self.List = collections.namedtuple(
            "List", "selection_color selection_cursor unselected_color"
        )


class DefaultTheme(Theme):
    def __init__(self):
        super().__init__()
        self.Question.mark_color = term.yellow
        self.Question.brackets_color = term.normal
        self.Question.default_color = term.normal
        self.Editor.opening_prompt_color = term.bright_black
        self.Checkbox.selection_color = term.blue
        self.Checkbox.selection_icon = ">"
        self.Checkbox.selected_icon = "⦿"
        self.Checkbox.selected_color = term.yellow + term.bold
        self.Checkbox.unselected_color = term.normal
        self.Checkbox.unselected_icon = "◌"
        self.List.selection_color = term.blue
        self.List.selection_cursor = ">"
        self.List.unselected_color = term.normal
