import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path

from .browser import *
from .param import *


def main() -> None:
    skip_sele = False
    if len(sys.argv) >= 2 and sys.argv[1] == "new":
        skip_sele = True

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Open Fuz Comic web with browser.
    fuz_web = fuz_browser()

    # Try to login with the email address and password for the previous login.
    fuz_web.login()

    # Pick items to download from your purchased titles.
    # Potential bug: comics purchased with gold coins may cause loading errors if
    #                the interface is different from the monthly magazine interface.
    picked_books = fuz_web.book_selector(skip_sele)
    pur_books_num = len(
        fuz_web.driver.find_elements(By.CSS_SELECTOR, "a[class^='Magazine']")
    )
    for picked_book in picked_books:
        # Handling the "Other: all free chapters of specified url" option.
        if picked_book == pur_books_num + 1:
            specified_books = get_manga_url_select_result()
            for specified_book in specified_books:
                # Jump to the specified page and detect if it is available
                fuz_web.jump_to_specified_manga(specified_book)
                if fuz_web.driver.find_elements(By.CSS_SELECTOR, "[class^='__500']"):
                    print(
                        bcolors.WARNING,
                        "[!] クエストキャンセル： " + str(specified_book) + " は一時的にご利用できません。",
                        bcolors.ENDC,
                    )
                else:
                    book_title = fuz_web.driver.find_element(By.CSS_SELECTOR, "h1[class^='title_detail_introduction__name']").text
                    chapters = fuz_web.get_free_chapter()
                    for chapter in chapters:
                        fuz_web.jump_to_specified_manga(specified_book)
                        fuz_web.jump_to_picked_chapter(int(chapter[0]))
                        fuz_web.download_book(chapter[1], book_title)
        # Handling the "Other: reader page url" option.
        elif picked_book == pur_books_num:
            specified_books = get_reader_url_select_result()
            for specified_book in specified_books:
                # Jump to the specified page and detect if it is available
                fuz_web.jump_to_manga_viewer(specified_book)
                if fuz_web.driver.find_elements(By.CSS_SELECTOR, "[class^='__500']"):
                    fuz_web.jump_to_book_viewer(specified_book)
                    if fuz_web.driver.find_elements(By.CSS_SELECTOR, "[class^='__500']"):
                        print(
                            bcolors.WARNING,
                            "[!] クエストキャンセル： " + str(specified_book) + " は一時的にご利用できません。",
                            bcolors.ENDC,
                        )
                    else:
                        fuz_web.download_book(subdir="@@RESERVED_AS_BOOK_TITLE_LA")
                else:
                    fuz_web.download_book("#" + str(specified_book), "@@RESERVED_AS_TITLE_LA")
        # Handling "Normal" options.
        else:
            picked_issues = fuz_web.issue_selector(picked_book, skip_sele)
            book_title = fuz_web.driver.find_element(By.CSS_SELECTOR, "h1[class^='magazine_issue_detail']").text
            for picked_issue in picked_issues:
                fuz_web.jump_to_picked_issue(picked_issue)
                fuz_web.download_book(subdir=book_title)

    print(bcolors.OKCYAN, "[+] クエスト完了", bcolors.ENDC)

    fuz_web.driver.quit()
