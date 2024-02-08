import yaml

from .param import *


class Context:
    def __init__(self) -> None:
        self.text = None

    def get_context(self) -> None:
        language = param.LANGUAGUE["language"]
        try:
            with open(
                param.CONTEXT_DIR + "/context-" + language + ".yaml",
                "r",
                encoding="utf8",
            ) as stream:
                self.text = yaml.load(stream, Loader=yaml.FullLoader)
        except:
            print(
                "[x] Error: Read "
                + param.CONTEXT_DIR
                + "/context-"
                + language
                + ".yaml failed"
            )
            raise

    def main_t(self, index) -> str:
        return self.text["main"][index]

    def browser_t(self, index) -> str:
        return self.text["browser"][index]

    def func_t(self, index) -> str:
        return self.text["func"][index]

    def mkpdf_t(self, index) -> str:
        return self.text["mkpdf"][index]

    def console_t(self, index) -> str:
        return self.text["console"][index]


context = Context()
