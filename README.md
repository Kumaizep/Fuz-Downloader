# Fuz-Downloader
This is a CLI tool to download comic from Fuz Comic.

## Usage

For first time use:

- The bot program is written in Python and tested in version `3.10.5`.It is recommended to run with a version no earlier than this

- This tool is based on the `selenium`, `webdriver_manager`, and `pypdf2` modules, please make sure the module is installed before running.
	- The easiest way to install those module is by using `pip`:

		`pip install selenium, webdriver_manager, pypdf2`

For execution:

1. Open a command line interpreter and change the directory to `{where_you_unzip_to}/Fuz-downloader-main/src`

2. Execute `python main.py`, then follow the instructions in the CLI to enter account information and select items to download

3. The downloaded file will be placed in `{where_you_unzip_to}/Fuz-downloader-main/output/{comic_title}`
, which contains the image file of each page and the integrated pdf file


