from PyPDF2 import PdfFileWriter, PdfFileReader
import img2pdf


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


def add_bookmark(path, bookmarks, title):
    print(
        "\r" + bcolors.OKBLUE,
        "[-]", title, "[marking]",
        bcolors.ENDC,
        end=''
    )
    reader = PdfFileReader(path, strict=False)
    writer = PdfFileWriter()
    for page in range(reader.numPages):
        writer.addPage(reader.getPage(page))
    for bookmark in bookmarks:

        writer.addBookmark(bookmark[0], int(bookmark[1]) - 1)
    with open(path, "wb") as file:
        writer.write(file)


def make_pdf(save_dir, title, page_num, bookmarks=[("-1", "-1")]):
    print(
        "\r" + bcolors.OKBLUE,
        "[-]", title, "[converting]",
        bcolors.ENDC,
        end=''
    )
    img_dir = save_dir + '/' + title
    pdf_path = save_dir + '/' + title + ".pdf"
    images = [
        img_dir + '/' + str(pn) + ".jpeg" for pn in range(page_num)
    ]
    dpix = dpiy = 200
    layout_fun = img2pdf.get_fixed_dpi_layout_fun((dpix, dpiy))
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(images, layout_fun=layout_fun))

    if bookmarks[0] != ("-1", "-1"):
        add_bookmark(pdf_path, bookmarks, title)
