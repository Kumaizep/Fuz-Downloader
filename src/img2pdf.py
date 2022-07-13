from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader

def add_bookmark(path, bookmarks):
	reader = PdfFileReader(path)
	writer = PdfFileWriter()
	for page in range(reader.numPages):
		writer.addPage(reader.getPage(page))
	for bookmark in bookmarks:
		writer.addBookmark(bookmark[0],int(bookmark[1]) - 1)
	with open(path, "wb") as file:
		writer.write(file)


def make_pdf(title, page_num, bookmarks=[("0", "0")], make_bookmark=True):
	save_dir = "../output/" + title
	images = [
		Image.open(save_dir + '/' + str(pn) + ".png") for pn in range(page_num)
	]
	pdf_path = save_dir + '/' + title + ".pdf"
	images[0].save(
		pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
	)
	if make_bookmark:
		add_bookmark(pdf_path, bookmarks)