# Fuz-Downloader
This is a CLI tool to download comic from Fuz Comic.

## Usage

For first time use:

- The bot program is written in Python and tested in version `3.10.5`.It is recommended to run with a version no earlier than this one.

- This tool is based on the `selenium`, `webdriver_manager`, `img2pdf`, `rich`, `blessed`, `inquirer`, `PyYAML`, and `pypdf2` modules.

- We Poetry to manage dependency, please confirm that Poetry has been installed.
	- One method to install Poetry is by using `pip`:

		`pip install poerty`

	- For other methods, see [here](https://python-poetry.org/docs/#installing-with-the-official-installer)

For execution:

1. Open a CLI and change the directory to `{where_you_unzip_to}/Fuz-downloader-main`.

2. Execute `poetry run fuzdownloader`, then follow the instructions in the CLI to enter account information and select items to download.
	- Before the first executeion, you need execute `poetry install` to ensure that the necessary modules are installed correctly.
	- For downloading only the latest issue of the magazine, you can execute `poetry run fuzdownloader new`

3. The downloaded file will be saved as `{where_you_unzip_to}/Fuz-downloader-main/output/{comic_title}.pdf`.

Language Setting:

- Execute `poetry run fuzdownloader set-lang {language code}` will change the default interface language to the specified language and run the downloader

- The following languages code are currently supported:
	- English: `en-US`
	- 繁體中文: `zh-TW`
	- 日本語: `ja-JP`

- To add or modify a language file, please fill in the format of the existing language file in `{where_you_unzip_to}/Fuz-downloader-main/data`.
	- For the case of adding language files, you should name the new language file `context-{language code}.yaml`, and write the new language code into the `list` in `language-setting.yaml`


