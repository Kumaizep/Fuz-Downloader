from typing import List
from pathlib import Path
from os.path import exists

from .param import *

def check_pdf_exist(path: str, filename: str) -> bool:
    return exists(path + '/' + filename)

def get_select_result(min_id: int, max_id: int) -> List[int]:
    need_select = True
    while need_select:
        try:
            result = list(
                map(int, input("どの本をダウンロードしますか？(数字のみ、スペースで区切る。例：1 0 3) ").split())
            )
            need_select = False
            for i in result:
                if i > max_id or i < min_id:
                    print(bcolors.WARNING, "[!] 無効な選択：", str(i), bcolors.ENDC)
                    need_select = True
        except:
            print(bcolors.WARNING, "[!] 指定されている形式で入力してください。", bcolors.ENDC)
    result.sort()
    return result


def get_reader_url_select_result() -> List[int]:
    print("<その他ーURLでダウンロード>")
    need_select = True
    while need_select:
        try:
            result = list(
                map(
                    int,
                    input(
                        "ダウンロードしたい本のURLの末尾にある番号を入力してください。\n (例えば、「ご注文はうさぎですか？１巻 第０話」のURLは「https://comic-fuz.com/manga/viewer/2443」なので、ダウンロードするときは「2443」と入力してください。スペースで区切る。) \n"
                    ).split(),
                )
            )
            need_select = False
            for i in result:
                if i < 0:
                    print(bcolors.WARNING, "[!] 無効な選択：", str(i), bcolors.ENDC)
                    need_select = True
        except:
            print(bcolors.WARNING, "[!] 指定されている形式で入力してください。", bcolors.ENDC)
    result.sort()
    return result

def get_manga_url_select_result() -> List[int]:
    print("<その他ーURLでダウンロード>")
    need_select = True
    while need_select:
        try:
            result = list(
                map(
                    int,
                    input(
                        "ダウンロードしたい作品のURLの末尾にある番号を入力してください。\n (例えば、「ご注文はうさぎですか？」のURLは「https://comic-fuz.com/manga/183」なので、ダウンロードするときは「183」と入力してください。スペースで区切る。) \n"
                    ).split(),
                )
            )
            need_select = False
            for i in result:
                if i < 0:
                    print(bcolors.WARNING, "[!] 無効な選択：", str(i), bcolors.ENDC)
                    need_select = True
        except:
            print(bcolors.WARNING, "[!] 指定されている形式で入力してください。", bcolors.ENDC)
    result.sort()
    return result


def get_account_info() -> List[str]:
    path = DATA_DIR + "/account"
    if exists(path):
        with open(path, "r") as file:
            data = file.readlines()
            data[0] = data[0][:-1]
        return data
    else:
        address = input("メールアドレス： ")
        password = input("パスワード： ")
        return [address, password]


def save_account_info(account) -> None:
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR + "/account", "w") as file:
        account[0] = account[0] + "\n"
        file.writelines(account)


def save_file(save_dir, page, data) -> None:
    path = save_dir + "/" + str(page) + ".jpeg"
    with open(path, "wb") as binary_file:
        binary_file.write(data)
