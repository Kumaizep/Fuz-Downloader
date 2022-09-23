import sys

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By

from .browser import *
from .console import *
from .context import *
from .func import *
from .param import *


class fuz_downloader:
    """docstring for fuz_downloader"""

    def __init__(self) -> None:
        Path(param.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        context.get_context()
        # Open Fuz Comic web with browser.
        self.fuz_web = fuz_browser()

    def terminal(self) -> None:
        self.fuz_web.terminal()

    def run(self, skip_sele: bool) -> None:
        # Try to login with the email address and password for the previous login.
        self.fuz_web.login()
        # Pick items to download from your purchased titles.
        # Potential bug: comics purchased with gold coins may cause loading errors if
        #                the interface is different from the monthly magazine interface.
        picked_books = self.fuz_web.book_selector(skip_sele)
        pur_books_num = len(self.fuz_web.find_elems_by_css("a[class^='Magazine']"))
        download_count = 0
        for picked_book in picked_books:
            if picked_book == pur_books_num + 1:
                # Handling the "Other: all free chapters of specified url" option.
                count = self.handle_catalog_url()
            elif picked_book == pur_books_num:
                # Handling the "Other: reader page url" option.
                count = self.handle_viewer_url()
            else:
                # Handling maganize options.
                count = self.handle_maganize(picked_book, skip_sele)
            download_count = download_count + count
            rich.cnsl.print("")

        rich.cnsl.print(param.SNORMAL + context.main_t("questDone"), style="sky_blue3")
        if download_count > 0:
            if param.DEBUG_MODE == True:
                rich.cnsl.print("Downloaded: {Num}".format(Num=download_count))
            else:
                open_sys_file_browser(param.OUTPUT_DIR)

    def handle_catalog_url(self) -> int:
        download_count = 0
        specified_books = get_manga_url_select_result()
        for specified_book in specified_books:
            # Jump to the specified page and detect if it is available
            self.fuz_web.jump_to_manga_catalog(specified_book)
            if not self.fuz_web.is_page_exist():
                self.fuz_web.jump_to_book_catalog(specified_book)
                if not self.fuz_web.is_page_exist():
                    rich.cnsl.print(
                        param.SWARNING
                        + context.main_t("500NotFound").format(
                            urlNumber=specified_book
                        ),
                        style="orange1",
                    )
                else:
                    request_id = self.fuz_web.get_book_detail_request()
                    message_json = self.fuz_web.protobuf_request_decode(request_id)
                    book_title, volumn_info = self.fuz_web.filter_book_detail(
                        message_json
                    )

                    rich.cnsl.rule(
                        "[bold sky_blue3]"
                        + book_title
                        + f" # book/{specified_book}"
                        + "[/bold sky_blue3]",
                        style="sky_blue3",
                    )
                    volumns = self.fuz_web.get_free_volumns(volumn_info)
                    rich.cnsl.print(
                        param.SNORMAL
                        + context.main_t("foundBook").format(
                            freeComicNumber=len(volumns)
                        ),
                        style="sky_blue3",
                    )
                    download_count = download_count + len(volumns)
                    for volumn in volumns:
                        self.fuz_web.jump_to_book_viewer(int(volumn[0]))
                        self.fuz_web.download_book(mark="", subdir=book_title)
            else:
                request_id = self.fuz_web.get_manga_detail_request()
                message_json = self.fuz_web.protobuf_request_decode(request_id)
                book_title, episodes_info = self.fuz_web.filter_manga_detail(
                    message_json
                )

                rich.cnsl.rule(
                    "[bold sky_blue3]"
                    + book_title
                    + f" # manga/{specified_book}"
                    + "[/bold sky_blue3]",
                    style="sky_blue3",
                )
                episodes = self.fuz_web.get_free_episodes(episodes_info)
                rich.cnsl.print(
                    param.SNORMAL
                    + context.main_t("foundBook").format(freeComicNumber=len(episodes)),
                    style="sky_blue3",
                )
                download_count = download_count + len(episodes)
                for episode in episodes:
                    self.fuz_web.jump_to_manga_viewer(int(episode[0]))
                    self.fuz_web.download_book(mark=episode[1], subdir=book_title)
        return download_count

    def handle_viewer_url(self) -> int:
        download_count = 0
        specified_books = get_reader_url_select_result()
        for specified_book in specified_books:
            # Jump to the specified page and detect if it is available
            self.fuz_web.jump_to_manga_viewer(specified_book)
            if not self.fuz_web.is_page_exist():
                self.fuz_web.jump_to_book_viewer(specified_book)
                if not self.fuz_web.is_page_exist():
                    rich.cnsl.print(
                        param.SWARNING
                        + context.main_t("500NotFound").format(
                            urlNumber=specified_book
                        ),
                        style="orange1",
                    )
                else:
                    self.fuz_web.download_book(subdir="@@RESERVED_AS_BOOK_TITLE_LA")
                    download_count = download_count + 1
            else:
                self.fuz_web.download_book(
                    "#" + str(specified_book), "@@RESERVED_AS_TITLE_LA"
                )
                download_count = download_count + 1
        return download_count

    def handle_maganize(self, picked_book: int, skip_sele: bool) -> int:
        picked_issues = self.fuz_web.issue_selector(picked_book, skip_sele)
        book_title = self.fuz_web.find_elems_by_css(
            "h1[class^='magazine_issue_detail']"
        ).text
        for picked_issue in picked_issues:
            self.fuz_web.jump_to_picked_issue(picked_issue)
            self.fuz_web.download_book(subdir=book_title)
        return len(picked_issues)
