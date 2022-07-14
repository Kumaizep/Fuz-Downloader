from fpdf import FPDF
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


def make_pdf(save_dir, title, page_num, size, bookmarks=[("-1", "-1")]):
	pdf_path = save_dir + '/' + title + ".pdf"
	pdf = FPDF('P', 'pt', size)
	# imagelist is the list with all image filenames
	imagelist = [
		Image.open(save_dir + '/' + str(pn) + ".png") for pn in range(page_num)
	]
	for image in imagelist:
	    pdf.add_page()
	    pdf.image(image, 0, 0, size[0], size[1])
	pdf.output(pdf_path)
	if make_bookmark != [("-1", "-1")]:
		add_bookmark(pdf_path, bookmarks)