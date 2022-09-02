# Fuz-Downloader
This is a CLI tool to download comic from Fuz Comic.

## Usage

For first time use:

- The bot program is written in Python and tested in version `3.10.5`.It is recommended to run with a version no earlier than this one.

- This tool is based on the `selenium`, `webdriver_manager`, `img2pdf`, `rich`, `blessed`, `inquirer`, `PyYAML`, and `pypdf2` modules.

- We Poetry to manage dependency, please confirm that Poetry has been installed.
	- One way to install Poetry is by using `pip`:

		`pip install poerty`

For execution:

1. Open a CLI and change the directory to `{where_you_unzip_to}/Fuz-downloader-main`.

2. Execute `poetry run fuzdownloader`, then follow the instructions in the CLI to enter account information and select items to download.
	- Before the first executeion, you need execute `poetry install` to ensure that the necessary modules are installed correctly.
	- For downloading only the latest issue of the magazine, you can execute `poetry run fuzdownloader new`

3. The downloaded file will be saved as `{where_you_unzip_to}/Fuz-downloader-main/output/{comic_title}.pdf`.


