import inquirer
import os
import yaml

from .theme import *


class Param(object):
    """docstring for param"""

    def __init__(self):
        Path(param.DATA_DIR).mkdir(parents=True, exist_ok=True)

        self.DEFAULT_LANGUAGE_SETTING = {
            "language": "ja-JP",
            "list": ["en-US", "ja-JP", "zh-TW"],
        }
        self.DEFAULT_OUTPUT_SETTING = {"dir": "./output"}

        self.CONTEXT_DIR = "./data/context"
        self.DATA_DIR = "./data/user"
        self.DEBUG_MODE = False
        self.IMG_SIZE = (1350, 1938)
        self.LANGUAGUE = self.load_language()
        self.OUTPUT_DIR = self.load_output_directory()
        self.VERSION = "1.1.0"

        self.SINDENT = "　　"
        self.SINPUT = "[[orange1]?[/orange1]] "
        self.SNORMAL = "[+] "
        self.SWARNING = "[!] "

    def load_language(self) -> str:
        try:
            with open(
                self.DATA_DIR + "/language-setting.yaml", "r", encoding="utf8"
            ) as stream:
                data = yaml.load(stream, Loader=yaml.FullLoader)
            return data
        except:
            data = self.DEFAULT_LANGUAGE_SETTING
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
            with open(
                self.DATA_DIR + "/language-setting.yaml", "w", encoding="utf8"
            ) as stream:
                yaml.dump(data, stream, Dumper=yaml.Dumper)
            return data

    def set_languague(self, language) -> None:
        if language in self.LANGUAGUE["list"]:
            self.LANGUAGUE["language"] = language
            try:
                with open(
                    self.DATA_DIR + "/language-setting.yaml", "w", encoding="utf8"
                ) as stream:
                    yaml.dump(self.LANGUAGUE, stream, Dumper=yaml.Dumper)
                print("[#] Message: Successfully set the language to " + language)
            except:
                print(
                    "[X] Error: Write "
                    + self.DATA_DIR
                    + "/language-setting.yaml failed"
                )
        else:
            print("[x] Error: Set language failed: invalid language.")

    def load_output_directory(self) -> str:
        try:
            with open(
                self.DATA_DIR + "/output-setting.yaml", "r", encoding="utf8"
            ) as stream:
                data = yaml.load(stream, Loader=yaml.FullLoader)
        except:
            data = os.path.abspath(os.path.expanduser(self.DEFAULT_OUTPUT_SETTING))
            with open(
                self.DATA_DIR + "/output-setting.yaml", "w", encoding="utf8"
            ) as stream:
                yaml.dump(data, stream, Dumper=yaml.Dumper)
        return data["dir"]

    def set_output_directory(self, dir: str) -> None:
        data = {"dir": os.path.abspath(os.path.expanduser(dir))}
        with open(
            self.DATA_DIR + "/output-setting.yaml", "w", encoding="utf8"
        ) as stream:
            yaml.dump(data, stream, Dumper=yaml.Dumper)
        print("[#] Message: Successfully set the language to " + data["dir"])
        self.OUTPUT_DIR = data["dir"]


param = Param()
