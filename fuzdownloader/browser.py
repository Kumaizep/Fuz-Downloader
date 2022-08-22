from typing import List
import time
import shutil
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .param import *
from .func import *
from .mkpdf import *

class fuz_browser:
    """docstring for fuz_browser"""

    def __init__(self) -> None:
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
            print(
                bcolors.WARNING,
                "[!] メールアドレス、もしくはパスワードを間違えています。再入力してください：",
                bcolors.ENDC,
            )
            self.account[0] = input("メールアドレス： ")
            self.account[1] = input("パスワード： ")
            self.try_login()
        print(bcolors.OKCYAN, "[+] ログインが完了しました。", bcolors.ENDC)
        save_account_info(self.account)

    def try_login(self) -> None:
        address = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        signin_buttom = self.driver.find_element(
            By.CSS_SELECTOR, "button[class^='signin_form']"
        )
        address.send_keys(self.account[0])
        password.send_keys(self.account[1])
        signin_buttom.click()
        time.sleep(2)

    def is_alert_present(self):
        try:
            alert = self.driver.switch_to.alert
            if self.driver.switch_to.alert.text == "メールアドレス、もしくはパスワードを間違えています。":
                alert.accept()
                return True
            else:
                print(bcolors.OKCYAN, "[+] 少々お待ちください。", bcolors.ENDC)
                time.sleep(10)
                self.try_login()
                return self.is_alert_present()
        except:
            return False

    def is_empty_input(self):
        if self.account[0] == "" or self.account[1] == "":
            return True
        else:
            return False

    def book_selector(self, skip: bool) -> List[int]:
        self.jump_to_purchased()
        books_title = self.driver.find_elements(By.CSS_SELECTOR, "h3")
        count = 0
        for book_title in books_title:
            print("(", count, ")", book_title.text)
            count += 1
        print("(", count, ")", "その他： リーダーページのURLでダウンロード")
        print("(", count + 1, ")", "その他： 指定されたURLのすべての無料単話")
        if skip:
            print(bcolors.OKCYAN, "[+] セレクター： ( 0 )", bcolors.ENDC)
            return [0]
        else:
            return get_select_result(0, count + 1)

    def jump_to_purchased(self) -> None:
        self.driver.get("https://comic-fuz.com/bookshelf")
        option_lables = self.driver.find_elements(By.CSS_SELECTOR, "label")
        option_lables[2].click()
        time.sleep(1)

    def issue_selector(self, book_id: int, skip: bool) -> List[int]:
        self.jump_to_picked_book(book_id)
        title = self.driver.find_element(By.CSS_SELECTOR, "h1")
        print("<", title.text.split()[0], ">")
        issues_title = self.driver.find_elements(By.CSS_SELECTOR, "h2")
        for count in range(3):
            print("(", count, ")", issues_title[count].text)
        if skip:
            print(bcolors.OKCYAN, "[+] セレクター： ( 0 )", bcolors.ENDC)
            return [0]
        else:
            return get_select_result(0, 2)

    def jump_to_picked_book(self, book_id: int) -> None:
        self.jump_to_purchased()
        purchased_books = self.driver.find_elements(
            By.CSS_SELECTOR, "a[class^='Magazine']"
        )
        purchased_books[book_id].click()
        time.sleep(1)

    def jump_to_picked_issue(self, issue_id: int) -> None:
        read_button = self.driver.find_elements(By.LINK_TEXT, "読む")
        read_button[issue_id + 1].click()
        time.sleep(1)

    def download_book(self, mark="", subdir="") -> None:
        info = self.load_book(mark)
        bookmarks = self.get_bookmarks()
        save_dir = OUTPUT_DIR
        if subdir == "@@RESERVED_AS_TITLE_LA":
            subdir = info[2]
        if subdir != "":
            save_dir = save_dir + "/" + subdir
            Path(save_dir).mkdir(parents=True, exist_ok=True)

        make_pdf(save_dir, info[0], int(info[1]), bookmarks)
        shutil.rmtree(OUTPUT_DIR + "/" + "TEMP" + info[0])
        print("\r" + bcolors.OKCYAN, "[+]", info[0], "[ Download Done ]", bcolors.ENDC)
        exit_button = self.driver.find_element(
            By.CSS_SELECTOR, "button[class^=ViewerHeader]"
        )
        exit_button.click()
        time.sleep(2)

    def load_book(self, mark="", need_load=True) -> List[str]:
        page_num = self.init_book()

        origin_title = self.driver.find_element(By.CSS_SELECTOR, "p[class^='ViewerHeader']").text
        title = origin_title + mark
        save_dir = OUTPUT_DIR + "/" + "TEMP" + title
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        if need_load:
            need_turning = True
            for pn in range(page_num):
                print(
                    "\r" + bcolors.OKBLUE,
                    "[-]" + title + " [ " + str(pn + 1) + " / " + str(page_num) + " ]",
                    bcolors.ENDC,
                    end="",
                )
                curr_page_uri = self.get_page_uri(pn)
                bytes = self.get_file_content_chrome(curr_page_uri)
                save_file(save_dir, pn, bytes)
                if need_turning == True:
                    self.driver.find_element(By.XPATH, "//body").send_keys(
                        Keys.ARROW_LEFT
                    )
                need_turning = not need_turning
        return [title, str(page_num), origin_title]

    def init_book(self) -> int:
        page = self.driver.find_element(
            By.CSS_SELECTOR, "p[class^='ViewerFooter_footer__page']"
        )
        while int(page.text[0:2]) != 1:
            self.driver.find_element(By.XPATH, "//body").send_keys(Keys.ARROW_RIGHT)
            page = self.driver.find_element(
                By.CSS_SELECTOR, "p[class^='ViewerFooter_footer__page']"
            )
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
        dailogs_name = self.driver.find_elements(
            By.CSS_SELECTOR, "p[class^=ViewerIndexModal_dialog__name]"
        )
        dailogs_index = self.driver.find_elements(
            By.CSS_SELECTOR, "p[class^=ViewerIndexModal_dialog__index]"
        )
        result = [[dn.text, di.text] for dn, di in zip(dailogs_name, dailogs_index)]
        return result

    def jump_to_reader(self, book_id:int) -> None:
        book_url = "https://comic-fuz.com/manga/viewer/" + str(book_id)
        self.driver.get(book_url)
        time.sleep(1)

    def get_free_chapter(self) -> List[List[str]]:
        chap_elems = self.driver.find_elements(
            By.CSS_SELECTOR, "a[class^=Chapter_chapter]"
        )
        free_chaps = list()
        chap_count = 0
        for chap_elem in chap_elems:
            elem_text = chap_elem.text.split('\n')
            if "無料" in elem_text:
                free_chaps.append([str(chap_count), elem_text[0]])
            chap_count = chap_count + 1

        return free_chaps

    def jump_to_specified_manga(self, manga_id:int) -> None:
        book_url = "https://comic-fuz.com/manga/" + str(manga_id)
        self.driver.get(book_url)
        time.sleep(1)

    def jump_to_picked_chapter(self, chapter_id: int) -> None:
        read_button = self.driver.find_elements(
            By.CSS_SELECTOR, "a[class^=Chapter_chapter]"
        )
        read_button[chapter_id].click()
        time.sleep(1)



