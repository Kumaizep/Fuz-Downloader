import base64
import inquirer
import os
import shutil
import time

from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .console import *
from .context import *
from .func import *
from .mkpdf import *
from .param import *
from .theme import *


class fuz_browser:
    """docstring for fuz_browser"""

    def __init__(self) -> None:
        rich.cnsl.rule(
            "[bold sky_blue3]" + context.browser_t("mainTitle") + "[/bold sky_blue3]",
            style="sky_blue3",
        )
        options = Options()
        options.add_argument("--headless")
        if shutil.which("chromedriver") is None:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
        else:
            self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(3)
        self.driver.get("https://comic-fuz.com/account/signin")
        self.account = get_account_info()

    def login(self) -> None:
        self.try_login()
        while self.is_alert_present() or self.is_empty_input():
            self.driver.refresh()
            rich.cnsl.print(SWARNING + context.browser_t("accountInfoError"), style="orange1")
            self.account["address"] = input(context.browser_t("accountAddress"))
            self.account["password"] = input(context.browser_t("accountPassword"))
            self.try_login()
        rich.cnsl.print(SNORMAL + context.browser_t("loginSuccess"), style="sky_blue3")
        save_account_info(self.account)
        time.sleep(1)

    def try_login(self) -> None:
        address = self.find_elem_by_css("input[type='email']")
        password = self.find_elem_by_css("input[type='password']")
        signin_buttom = self.find_elem_by_css("button[class^='signin_form']")
        address.send_keys(self.account["address"])
        password.send_keys(self.account["password"])
        signin_buttom.click()
        time.sleep(2)

    def is_alert_present(self):
        try:
            alert = self.driver.switch_to.alert
            if alert.text == "メールアドレス、もしくはパスワードを間違えています。":
                alert.accept()
                return True
            else:
                rich.cnsl.print(SNORMAL + context.browser_t("waitAMoment"), style="sky_blue2")
                alert.accept()
                time.sleep(10)
                self.try_login()
                return self.is_alert_present()
        except:
            return False

    def is_empty_input(self):
        if self.account["address"] == "" or self.account["password"] == "":
            return True
        else:
            return False

    # def book_selector(self, skip: bool) -> List[int]:
    #     self.jump_to_purchased()
    #     books_title = self.find_elems_by_css("h3")
    #     count = 0
    #     for book_title in books_title:
    #         print("(", count, ")", book_title.text)
    #         count += 1
    #     print("(", count, ")", "その他： リーダーページのURLでダウンロード")
    #     print("(", count + 1, ")", "その他： 指定されたURLのすべての無料単話")
    #     if skip:
    #         rich.cnsl.print("[+] セレクター： ( 0 )", style="sky_blue3")
    #         return [0]
    #     else:
    #         return get_select_result(0, count + 1)

    def book_selector(self, skip: bool) -> List[int]:
        self.jump_to_purchased()
        books_title = self.find_elems_by_css("h3")
        books_num = len(books_title)
        books_title_list = [(books_title[1].text, i) for i in range(books_num)]
        books_title_list.append((context.browser_t("otherViewerUrl"), books_num))
        books_title_list.append((context.browser_t("otherCatalogUrl"), books_num + 1))

        if skip:
            rich.cnsl.print(
                SNORMAL + context.browser_t("autoSelector") + books_title_list[0][0], 
                style="sky_blue3"
            )
            return [0]
        else:
            questions = [
                inquirer.Checkbox(
                    name="picked_books",
                    message=context.browser_t("chooseDownloadItem"),
                    choices=books_title_list,
                )
            ]
            return inquirer.prompt(questions, theme=DefaultTheme())["picked_books"]

    def jump_to_purchased(self) -> None:
        self.driver.get("https://comic-fuz.com/bookshelf")
        time.sleep(1)
        option_lables = self.find_elems_by_css("label")
        option_lables[2].click()
        time.sleep(1)

    def issue_selector(self, book_id: int, skip: bool) -> List[int]:
        self.jump_to_picked_book(book_id)
        title = self.find_elem_by_css("h1")
        rich.csnl.rule(
            "[bold sky_blue3]< " + title.text.split()[0] + " >[/bold sky_blue3]",
            style="sky_blue3",
        )
        issues_title = self.find_elems_by_css("h2")
        issues_title_list = [(issues_title[i].text, i) for i in range(3)]

        if skip:
            csnl.print("[+] セレクター： " + issues_title[0], style="sky_blue3")
            return [0]
        else:
            questions = [
                inquirer.Checkbox(
                    name="picked_issues",
                    message=context.browser_t("chooseDownloadIssue"),
                    choices=issues_title_list,
                )
            ]
            return inquirer.prompt(questions, theme=DefaultTheme())["picked_issues"]

    def jump_to_picked_book(self, book_id: int) -> None:
        self.jump_to_purchased()
        purchased_books = self.find_elems_by_css("a[class^='Magazine']")
        purchased_books[book_id].click()
        time.sleep(1)

    def jump_to_picked_issue(self, issue_id: int) -> None:
        read_button = self.driver.find_elements(By.LINK_TEXT, "読む")
        read_button[issue_id + 1].click()
        time.sleep(1)

    def download_book(self, mark="", subdir="") -> None:
        title = self.get_book_title(mark)
        save_dir = self.gen_save_dir(title[1], subdir)
        full_path = os.path.abspath(os.getcwd()) + save_dir[1:]

        rich.cnsl.print("[+] " + title[0][:60] + "：", style="sky_blue3")

        if self.is_book_exist(save_dir, title[0]):
            rich.cnsl.print(SINDENT + context.browser_t("pdfExisted"), style="sky_blue3")
            return

        page_num = self.load_book(title[0])
        rich.update_single_progress(content="Processing")
        bookmarks = self.get_bookmarks()

        make_pdf(save_dir, title[0], page_num, bookmarks)
        shutil.rmtree(OUTPUT_DIR + "/" + "TEMP" + title[0])

        rich.update_single_progress(content="Done")
        rich.terminal_single_progress()
        styled_full_path = "[light_steel_blue underline]" + full_path + "[/light_steel_blue underline]"
        rich.cnsl.print(
            SINDENT + context.browser_t("pdfSaved").format(save_path=styled_full_path), 
            style="sky_blue3"
        )

        exit_button = self.find_elem_by_css("button[class^=ViewerHeader]")
        exit_button.click()
        time.sleep(2)

    def get_book_title(self, mark: str) -> List[str]:
        origin_title = self.find_elem_by_css("p[class^='ViewerHeader']").text
        title = origin_title + mark
        return [title, origin_title]

    def gen_save_dir(self, origin_title: str, subdir: str) -> str:
        save_dir = OUTPUT_DIR
        if subdir == "@@RESERVED_AS_TITLE_LA":
            subdir = origin_title
        elif subdir == "@@RESERVED_AS_BOOK_TITLE_LA":
            tmpdir = origin_title.split("\u3000")
            subdir = tmpdir[0]
            tmpdir = tmpdir[1:-1]
            for td in tmpdir:
                subdir = subdir + "\u3000" + td
        if subdir != "":
            save_dir = save_dir + "/" + subdir
            Path(save_dir).mkdir(parents=True, exist_ok=True)
        return save_dir

    def is_book_exist(self, path: str, title: str) -> bool:
        return check_pdf_exist(path, title + ".pdf")

    def load_book(self, title: str, need_load=True) -> int:
        page_num = self.init_book()

        save_dir = OUTPUT_DIR + "/" + "TEMP" + title
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        if need_load:
            rich.create_single_progress(content="Downloading", total=page_num)
            need_turning = True
            for pn in range(page_num):
                rich.advance_single_progress()
                curr_page_uri = self.get_page_uri(pn)
                bytes = self.get_file_content_chrome(curr_page_uri)
                save_file(save_dir, pn, bytes)
                if need_turning == True:
                    self.driver.find_element(By.XPATH, "//body").send_keys(
                        Keys.ARROW_LEFT
                    )
                need_turning = not need_turning
        return page_num

    def init_book(self) -> int:
        page = self.find_elem_by_css("p[class^='ViewerFooter_footer__page']")
        while int(page.text[0:2]) != 1:
            self.driver.find_element(By.XPATH, "//body").send_keys(Keys.ARROW_RIGHT)
            page = self.find_elem_by_css("p[class^='ViewerFooter_footer__page']")
        page_num = int(page.text[4:]) - 1
        return page_num

    def get_page_uri(self, page: int) -> str:
        try:
            page_img = self.driver.find_element(
                By.XPATH, "//img[@alt='page_" + str(page) + "']"
            )
        except:
            self.driver.find_element(By.XPATH, "//body").send_keys(Keys.ARROW_LEFT)
            page_img = self.driver.find_element(
                By.XPATH, "//img[@alt='page_" + str(page) + "']"
            )
        page_src = page_img.get_attribute("src")
        while page_src == None:
            page_src = page_img.get_attribute("src")
        return page_src

    def get_file_content_chrome(self, uri: str) -> bytes:
        result = self.driver.execute_async_script(
            """
            var uri = arguments[0];
            var callback = arguments[1];
            var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
            var xhr = new XMLHttpRequest();
            xhr.responseType = 'arraybuffer';
            xhr.onload = function(){ callback(toBase64(xhr.response)) };
            xhr.onerror = function(){ callback(xhr.status) };
            xhr.open('GET', uri);
            xhr.send();
            """,
            uri,
        )
        if type(result) == int:
            raise Exception("Request failed with status %s" % result)
        return base64.b64decode(result)

    def get_bookmarks(self) -> List[List[str]]:
        try:
            catalog = self.driver.find_element(By.LINK_TEXT, "目次")
        except:
            return [("-1", "-1")]
        self.driver.execute_script("arguments[0].click();", catalog)
        dailogs_name = self.find_elems_by_css("p[class^=ViewerIndexModal_dialog__name]")
        dailogs_index = self.find_elems_by_css(
            "p[class^=ViewerIndexModal_dialog__index]"
        )
        result = [[dn.text, di.text] for dn, di in zip(dailogs_name, dailogs_index)]
        return result

    def jump_to_manga_viewer(self, book_id: int) -> None:
        book_url = "https://comic-fuz.com/manga/viewer/" + str(book_id)
        self.driver.get(book_url)
        time.sleep(1)

    def jump_to_book_viewer(self, book_id: int) -> None:
        book_url = "https://comic-fuz.com/book/viewer/" + str(book_id)
        self.driver.get(book_url)
        time.sleep(1)

    def get_free_chapter(self) -> List[List[str]]:
        chap_elems = self.find_elems_by_css("a[class^=Chapter_chapter]")
        chap_names = self.find_elems_by_css("h3[class^=Chapter_chapter__name]")
        chap_subnames = self.find_elems_by_css("p[class^=Chapter_chapter__subName]")
        chap_count = 0
        free_chaps = list()
        for chap_elem in chap_elems:
            elem_text = chap_elem.text.split("\n")
            if "無料" in elem_text:
                free_chaps.append(
                    [
                        str(chap_count),
                        chap_names[chap_count].text + chap_subnames[chap_count].text,
                    ]
                )
            chap_count = chap_count + 1

        return free_chaps

    def jump_to_specified_manga(self, manga_id: int) -> None:
        book_url = "https://comic-fuz.com/manga/" + str(manga_id)
        self.driver.get(book_url)
        time.sleep(1)

    def jump_to_picked_chapter(self, chapter_id: int) -> None:
        read_button = self.find_elems_by_css("a[class^=Chapter_chapter]")
        read_button[chapter_id].click()
        time.sleep(1)

    def is_page_exist(self) -> bool:
        if self.find_elems_by_css("[class^='__500']"):
            return False
        else:
            return True

    def find_elem_by_css(self, css_selector: str):
        return self.driver.find_element(By.CSS_SELECTOR, css_selector)

    def find_elems_by_css(self, css_selector: str) -> List:
        return self.driver.find_elements(By.CSS_SELECTOR, css_selector)
