import yaml
import inquirer

from .param import *
from .theme import *


class Context:
    def __init__(self) -> None:
        self.text = None
        self.language_setting = self.get_language_setting()
        self.get_context(self.language_setting["language"])

    def get_language_setting(self) -> str:
        try:
            with open(DATA_DIR + "/language-setting.yaml", "r") as stream:
                data = yaml.load(stream, Loader=yaml.FullLoader)
            return data
        except:
            data = DEFAULT_LANGUAGE_SETTING
            # print("[I] 言語プロファイルなし / 缺乏語言設定檔 / No language profile")
            questions = [
                inquirer.List(
                    "language",
                    message="言語を選択してください / 請選擇語言 / Please select language",
                    choices=["ja-JP", "zh-TW", "en-US"],
                )
            ]
            data["language"] = inquirer.prompt(questions, theme=DefaultTheme())[
                "language"
            ]
            with open(DATA_DIR + "/language-setting.yaml", "w") as stream:
                yaml.dump(data, stream, Dumper=yaml.Dumper)
            return data

    def get_context(self, language) -> None:
        try:
            with open(DATA_DIR + "/context-" + language + ".yaml", "r") as stream:
                self.text = yaml.load(stream, Loader=yaml.FullLoader)
        except:
            print(
                "[x] Error: Read " + DATA_DIR + "/context-" + language + ".yaml failed"
            )
            raise

    def set_languague(self, language) -> None:
        if language in self.language_setting["list"]:
            self.language_setting["language"] = language
            try:
                with open(DATA_DIR + "/language-setting.yaml", "w") as stream:
                    yaml.dump(self.language_setting, stream, Dumper=yaml.Dumper)
            except:
                print("[X] Error: Write " + DATA_DIR + "/language-setting.yaml failed")
            self.get_context(self.language_setting["language"])
        else:
            print("[x] Error: Set language failed: invalid language.")

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
