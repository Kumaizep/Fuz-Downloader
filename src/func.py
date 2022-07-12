from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import base64

def get_page_uri(driver, page):
	page_img = driver.find_element(By.XPATH, "//img[@alt='page_" + str(page) + "']")
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
	if type(result) == int :
		raise Exception("Request failed with status %s" % result)
	return base64.b64decode(result)

def save_file(save_dir, page, data):
	path = save_dir + "/" + str(page) + ".png"
	with open(path, 'wb') as binary_file:
		binary_file.write(data)

def make_pdf(title, page_num):
	save_dir = "../output/" + title
	images = [
		Image.open(save_dir + '/' + str(pn) + ".png") for pn in range(page_num)
	]
	pdf_path = save_dir + '/' + title + ".pdf"
	images[0].save(
		pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
	)

