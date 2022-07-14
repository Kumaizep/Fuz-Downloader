from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import shutil

from func import *
from mkpdf import *

Path("../output").mkdir(parents=True, exist_ok=True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(1)
# driver.maximize_window()
driver.get("https://comic-fuz.com/account/signin")

account = get_account_info()
login(driver, account)

jump_to_purchased(driver)
picked_books = book_selector(driver)
for book_id in picked_books:
	jump_to_purchased(driver)
	purchased_books = driver.find_elements(By.CSS_SELECTOR, "a[class^='Magazine']")

	if book_id == len(purchased_books):
		# print(bcolors.WARNING, "[#] この機能はまだ利用できません", bcolors.ENDC)
		# pass
		print("<その他ーURLからダウンロードします>")
		specified_book = other_selector()
		for book_uid in specified_book:
			book_url = "https://comic-fuz.com/manga/viewer/" + str(book_uid)
			driver.get(book_url)
			time.sleep(1)
			if driver.find_elements(By.CSS_SELECTOR, "[class^='__500']"):
				print(
					bcolors.WARNING, 
					"[!] クエストキャンセル：", book_url, "は一時的にご利用できません。", 
					bcolors.ENDC
				)
			else:
				info = load_book(driver, "#" + str(book_uid), need_load=False)
				make_pdf(OUTPUT_DIR, info[0], int(info[1]))
				shutil.rmtree(OUTPUT_DIR + "/" + info[0])
				print(
					'\r' + bcolors.OKCYAN, 
					"[+]", info[0], "[Download Done]", 
					bcolors.ENDC
				)
	else:
		purchased_books[book_id].click()
		time.sleep(1)
		title = driver.find_element(By.CSS_SELECTOR, "h1")
		print("<", title.text.split()[0], ">")
		picked_issues = issue_selector(driver)
		for issue_id in picked_issues:
			read_button = driver.find_elements(By.LINK_TEXT, "読む")
			read_button[issue_id + 1].click()
			time.sleep(1)
			info = load_book(driver, need_load=False)
			bookmarks = get_bookmarks(driver)
			make_pdf(OUTPUT_DIR, info[0], int(info[1]), bookmarks)
			shutil.rmtree(OUTPUT_DIR + "/" + info[0])
			print(
				'\r' + bcolors.OKCYAN, 
				"[+]", info[0], "[Download Done]", 
				bcolors.ENDC
			)
			exit_button = driver.find_element(By.CSS_SELECTOR, "button[class^=ViewerHeader]")
			exit_button.click()
			time.sleep(2)

print(bcolors.OKCYAN, "[+] クエスト ドネ", bcolors.ENDC)

