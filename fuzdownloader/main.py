from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path

from .browser import *
from .param import *


def main() -> None:
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    fuz_web = fuz_browser()

    account = get_account_info()
    fuz_web.login(account)

    picked_books = fuz_web.book_selector()
    pur_books_num = len(
        fuz_web.driver.find_elements(By.CSS_SELECTOR, "a[class^='Magazine']")
    )
    for picked_book in picked_books:
        if picked_book == pur_books_num:
            specified_books = get_url_select_result()
            for specified_book in specified_books:
                fuz_web.jump_to_viewer(specified_book)
                if fuz_web.driver.find_elements(By.CSS_SELECTOR, "[class^='__500']"):
                    print(
                        bcolors.WARNING,
                        "[!] クエストキャンセル： " + str(specified_book) + " は一時的にご利用できません。",
                        bcolors.ENDC,
                    )
                else:
                    fuz_web.download_book("#" + str(specified_book))
        else:
            picked_issues = fuz_web.issue_selector(picked_book)
            for picked_issue in picked_issues:
                fuz_web.jump_to_picked_issue(picked_issue)
                fuz_web.download_book()

    print(bcolors.OKCYAN, "[+] クエスト完了", bcolors.ENDC)

    fuz_web.driver.quit()
