from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from os.path import exists
from pathlib import Path
import time
import base64

OUTPUT_DIR = "./output"
DATA_DIR = "./data"
IMG_SIZE = (1350, 1938)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_account_info():
    path = DATA_DIR + "/account"
    if exists(path):
        with open(path, 'r') as file:
            data = file.readlines()
            data[0] = data[0][:-1]
        return data
    else:
        address = input("メールアドレス： ")
        password = input("パスワード： ")
        return [address, password]


def save_account_info(account):
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR + "/account", 'w') as file:
        account[0] = account[0] + '\n'
        file.writelines(account)


def try_login(driver, account):
    address = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    signin_buttom = driver.find_element(
        By.CSS_SELECTOR, "button[class^='signin_form']")
    address.send_keys(account[0])
    password.send_keys(account[1])
    signin_buttom.click()
    time.sleep(2)


def login(driver, account):
    try_login(driver, account)
    while is_alert_present(driver, account) or account[0] == '' or account[1] == '':
        driver.refresh()
        print(
            bcolors.WARNING,
            "[!] メールアドレス、もしくはパスワードを間違えています。再入力してください：",
            bcolors.ENDC
        )
        account[0] = input("メールアドレス： ")
        account[1] = input("パスワード： ")
        try_login(driver, account)
    print(bcolors.OKCYAN, "[+] ログインが完了しました。", bcolors.ENDC)
    save_account_info(account)


def is_alert_present(driver, account):
    try:
        alert = driver.switch_to.alert
        if driver.switch_to.alert.text == "メールアドレス、もしくはパスワードを間違えています。":
            alert.accept()
            return True
        else:
            print(
                bcolors.OKCYAN,
                "[+] 少々お待ちください。",
                bcolors.ENDC
            )
            time.sleep(10)
            try_login(driver, account)
            return is_alert_present(driver, account)
    except:
        return False


def jump_to_purchased(driver):
    driver.get("https://comic-fuz.com/bookshelf")
    option_lable = driver.find_elements(By.CSS_SELECTOR, "label")
    option_lable[2].click()
    time.sleep(1)


def get_select_result(min_id, max_id):
    need_select = True
    while need_select:
        try:
            result = list(
                map(int, input("どの本をダウンロードしますか？(数字のみ、スペースで区切る。例：1 0 3) ").split()))
            need_select = False
            for i in result:
                if i > max_id or i < min_id:
                    print(bcolors.WARNING, "[!] 無効な選択：", str(i), bcolors.ENDC)
                    need_select = True
        except:
            print(bcolors.WARNING, "[!] 指定られたフォームを入力してください", bcolors.ENDC)
    result.sort()
    return result


def book_selector(driver):
    books_title = driver.find_elements(By.CSS_SELECTOR, "h3")
    count = 0
    for book_title in books_title:
        print('(', count, ')', book_title.text)
        count += 1
    print('(', count, ')', "その他ーURLでダウンロード")
    return get_select_result(0, count)


def issue_selector(driver):
    issues_title = driver.find_elements(By.CSS_SELECTOR, "h2")
    for count in range(3):
        print('(', count, ')', issues_title[count].text)
    return get_select_result(0, 2)


def other_selector():
    need_select = True
    while need_select:
        try:
            result = list(map(int, input(
                "ダウンロードしたい本のURLの末尾にある番号を入力してください。\n (例えば、「ご注文はうさぎですか？１巻 第０話」のURLは「https://comic-fuz.com/manga/viewer/2443」なので、ダウンロードするときは「2443」と入力してください。スペースで区切る。) \n").split()))
            need_select = False
            for i in result:
                if i < 0:
                    print(bcolors.WARNING, "[!] 無効な選択：", str(i), bcolors.ENDC)
                    need_select = True
        except:
            print(bcolors.WARNING, "[!] 指定られたフォームを入力してください", bcolors.ENDC)
    result.sort()
    return result


def init_book(driver):
    page = driver.find_element(
        By.CSS_SELECTOR, "p[class^='ViewerFooter_footer__page']")
    while int(page.text[0:2]) != 1:
        driver.find_element(By.XPATH, "//body").send_keys(Keys.ARROW_RIGHT)
        page = driver.find_element(
            By.CSS_SELECTOR, "p[class^='ViewerFooter_footer__page']")
    page_num = int(page.text[4:]) - 1
    return page_num


def load_book(driver, mark="", need_load=True):
    page_num = init_book(driver)

    title = driver.find_element(
        By.CSS_SELECTOR, "p[class^='ViewerHeader']").text + mark
    save_dir = OUTPUT_DIR + "/" + title
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    if need_load:
        need_turning = True
        for pn in range(page_num):
            print(
                "\r" + bcolors.OKBLUE,
                "[-]", title, "[", str(pn + 1), '/', str(page_num), ']',
                bcolors.ENDC,
                end=''
            )
            curr_page_uri = get_page_uri(driver, pn)
            bytes = get_file_content_chrome(driver, curr_page_uri)
            save_file(save_dir, pn, bytes)
            if need_turning == True:
                driver.find_element(
                    By.XPATH, "//body").send_keys(Keys.ARROW_LEFT)
            need_turning = not need_turning

    return (title, str(page_num))


def get_page_uri(driver, page):
    page_img = driver.find_element(
        By.XPATH, "//img[@alt='page_" + str(page) + "']")
    page_src = page_img.get_attribute("src")
    while page_src == None:
        page_src = page_img.get_attribute("src")
    return page_src


def get_file_content_chrome(driver, uri):
    result = driver.execute_async_script("""
		var uri = arguments[0];
		var callback = arguments[1];
		var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
		var xhr = new XMLHttpRequest();
		xhr.responseType = 'arraybuffer';
		xhr.onload = function(){ callback(toBase64(xhr.response)) };
		xhr.onerror = function(){ callback(xhr.status) };
		xhr.open('GET', uri);
		xhr.send();
		""", uri)
    if type(result) == int:
        raise Exception("Request failed with status %s" % result)
    return base64.b64decode(result)


def save_file(save_dir, page, data):
    path = save_dir + "/" + str(page) + ".jpeg"
    with open(path, 'wb') as binary_file:
        binary_file.write(data)


def get_bookmarks(driver):
    catalog = driver.find_element(By.LINK_TEXT, "目次")
    catalog.click()
    dailogs_name = driver.find_elements(
        By.CSS_SELECTOR, "p[class^=ViewerIndexModal_dialog__name]")
    dailogs_index = driver.find_elements(
        By.CSS_SELECTOR, "p[class^=ViewerIndexModal_dialog__index]")
    result = [[dn.text, di.text]
              for dn, di in zip(dailogs_name, dailogs_index)]
    return result
