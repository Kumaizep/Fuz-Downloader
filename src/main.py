from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time

from func import *

# Account info
address  = ""
password = ""

download_number = 1

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://comic-fuz.com/account/signin")

signin = driver.find_elements(By.CLASS_NAME, "signin_form__input__2XHsd")
signin[0].send_keys(address)
signin[1].send_keys(password)
time.sleep(1)
signin_buttom = driver.find_element(By.CLASS_NAME, "signin_form__button__ph56X")
signin_buttom.click()

magazines = ["まんがタイムきらら", "まんがタイムきららMAX", "まんがタイムきららキャラット", "まんがタイムきららフォワード"]
# magazines = ["まんがタイムきららフォワード"]

Path("../output").mkdir(parents=True, exist_ok=True)


for maga_name in magazines:
	time.sleep(1)
	plan_link = driver.find_element(By.LINK_TEXT, "月額プラン")
	plan_link.click()
	time.sleep(1)

	maga_link = driver.find_element(By.LINK_TEXT, maga_name)
	maga_link.click()

	for num in range(1, Download_number):
		time.sleep(2)
		read_button = driver.find_elements(By.LINK_TEXT, "読む")
		read_button[num].click()
		time.sleep(2)

		title = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/p").text
		save_dir = "../output/" + title
		Path(save_dir).mkdir(parents=True, exist_ok=True)
		page_count = driver.find_element(By.XPATH, "/html/body/div/div/div[3]/p")
		while int(page_count.text[0:2]) != 1:
			driver.find_element(By.XPATH, "//body").send_keys(Keys.ARROW_RIGHT)
			page_count = driver.find_element(By.XPATH, "/html/body/div/div/div[3]/p")
		page_num = int(page_count.text[3:]) - 1

		need_turning = True
		for pn in range(page_num):
			print('\r' + title + " [" + str(pn) + '/' + str(page_num) + ']', end='')
			curr_page_uri = get_page_uri(driver, pn)
			bytes = get_file_content_chrome(driver, curr_page_uri)
			save_file(save_dir, pn, bytes)
			if need_turning == True:
				driver.find_element(By.XPATH, "//body").send_keys(Keys.ARROW_LEFT)
				need_turning = False
			else:
				need_turning = True

		make_pdf(title, page_num)
		print('\r' + title + " [Download Done]")
		exit_button = driver.find_element(By.XPATH, "//button")
		exit_button.click()
