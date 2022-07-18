from typing import List

from PyPDF2 import PdfFileWriter, PdfFileReader
import img2pdf

from .param import *


def add_bookmark(path: str, bookmarks: List[List[str]], title: str) -> None:
    print("\r" + bcolors.OKBLUE, "[-]", title, "[marking]", bcolors.ENDC, end="")
    reader = PdfFileReader(path, strict=False)
    writer = PdfFileWriter()
    for page in range(reader.numPages):
        writer.addPage(reader.getPage(page))
    for bookmark in bookmarks:

        writer.addBookmark(bookmark[0], int(bookmark[1]) - 1)
    with open(path, "wb") as file:
        writer.write(file)


def make_pdf(save_dir: str, title: str, page_num: int, bookmarks=[["-1", "-1"]]) -> None:
    print("\r" + bcolors.OKBLUE, "[-]", title, "[converting]", bcolors.ENDC, end="")
    img_dir = save_dir + "/" + title
    pdf_path = save_dir + "/" + title + ".pdf"
    images = [img_dir + "/" + str(pn) + ".jpeg" for pn in range(page_num)]
    dpix = dpiy = 200
    layout_fun = img2pdf.get_fixed_dpi_layout_fun((dpix, dpiy))
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(images, layout_fun=layout_fun))

    if bookmarks[0] != ["-1", "-1"]:
        add_bookmark(pdf_path, bookmarks, title)
