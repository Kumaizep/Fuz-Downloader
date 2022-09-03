import yaml

from typing import List
from pathlib import Path
from os.path import exists

from .console import *
from .context import *
from .param import *


def check_pdf_exist(path: str, filename: str) -> bool:
    return exists(path + "/" + filename)


# def get_select_result(min_id: int, max_id: int) -> List[int]:
#     need_select = True
#     while need_select:
#         try:
#             result = list(
#                 map(int, input("どの本をダウンロードしますか？(数字のみ、スペースで区切る。例：1 0 3) ").split())
#             )
#             need_select = False
#             for i in result:
#                 if i > max_id or i < min_id:
#                     rich.cnsl.print("[!] 無効な選択： " + str(i), style="orange1")
#                     need_select = True
#         except:
#             rich.cnsl.print("[!] 指定されている形式で入力してください。", style="orange1")
#     result.sort()
#     return result


def get_reader_url_select_result() -> List[int]:
    rich.panel(
        "[bold default]"
        + context.func_t("keyInViewerUrl")
        + "[/bold default]\n\n[default]"
        + context.func_t("keyInViewerUrlExample")
        + "[/default]",
        title="[bold]" + context.func_t("keyInViewerUrlTitle") + "[/bold]",
        style="sky_blue3",
    )
    need_select = True
    while need_select:
        try:
            result = list(
                map(
                    int,
                    rich.cnsl.input(SINPUT + context.func_t("urlNumber")).split(),
                )
            )
            need_select = False
            for i in result:
                if i < 0:
                    rich.cnsl.print(
                        SWARNING + context.func_t("invalidChoice") + str(i),
                        style="orange1",
                    )
                    need_select = True
        except:
            rich.cnsl.print(SWARNING + context.func_t("invalidFormat"), style="orange1")
    result.sort()
    return result


def get_manga_url_select_result() -> List[int]:
    rich.panel(
        "[bold default]"
        + context.func_t("keyInCatalogUrl")
        + "[/bold default]\n\n[default]"
        + context.func_t("keyInCatalogUrlExample")
        + "[/default]",
        title="[bold]" + context.func_t("keyInCatalogUrlTitle") + "[/bold]",
        style="sky_blue3",
    )
    need_select = True
    while need_select:
        try:
            result = list(
                map(
                    int,
                    rich.cnsl.input(SINPUT + context.func_t("urlNumber")).split(),
                )
            )
            need_select = False
            for i in result:
                if i < 0:
                    rich.cnsl.print(
                        SWARNING + context.func_t("invalidChoice") + str(i),
                        style="orange1",
                    )
                    need_select = True
        except:
            rich.cnsl.print(SWARNING + context.func_t("invalidFormat"), style="orange1")
    result.sort()
    return result


# def get_account_info() -> List[str]:
#     path = DATA_DIR + "/account"
#     if exists(path):
#         with open(path, "r") as file:
#             data = file.readlines()
#             data[0] = data[0][:-1]
#         return data
#     else:
#         address = input("メールアドレス： ")
#         password = input("パスワード： ")
#         return [address, password]
def get_account_info():
    path = DATA_DIR + "/account.yaml"
    if exists(path):
        with open(path, "r") as stream:
            data = yaml.load(stream, Loader=yaml.FullLoader)
        return data
    else:
        address = input(context.func_t("accountAddress"))
        password = input(context.func_t("accountPassword"))
        return {"address": address, "password": password}


def save_account_info(account) -> None:
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR + "/account.yaml", "w") as stream:
        yaml.dump(account, stream, Dumper=yaml.Dumper)


def save_file(save_dir, page, data) -> None:
    path = save_dir + "/" + str(page) + ".jpeg"
    with open(path, "wb") as binary_file:
        binary_file.write(data)
