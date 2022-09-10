# Fuz-Downloader
A python-based CLI interactive program for downloading viewable comics from COMIC FUZ.

## Intro

This program is written in Python and tested in version `3.10.5`.It is recommended to run with a version no earlier than this one. It mainly depends on `selenium`, `webdriver_manager` manager, and several other libraries, and use `Poetry` to manage dependency, please confirm that `Poetry` has been installed.

## Installation

### Manual installation

Download the zip file from [here](https://github.com/Kumaizep/Fuz-downloader/archive/refs/heads/main.zip) and unzip it anywhere you want. You might need to install `Poetry` to manage and execute it.
	- One simple (but not recommended) way to install Poetry is by using `pip`:
		`pip install poerty`
	- For other methods, see [here](https://python-poetry.org/docs/#installing-with-the-official-installer)


### Script installation (Experimental)
	```
	curl -LO https://github.com/Kumaizep/Fuz-Downloader/releases/download/latest-dev/fuz-donwloader && chmod +x fuz-donwloader && mv fuz-donwloader ~/.local/bin && fuz-donwloader -i
	```


## Usage

### Using poetry (Manual)

For execution:

1. Open a CLI and change the directory to `{where_you_unzip_to}/Fuz-downloader-main`.

2. Execute `poetry run fuzdownloader`, then follow the instructions in the CLI to enter account information and select items to download.
	- Before the first executeion or update to new version, you need execute `poetry install` to ensure that the necessary modules are installed correctly.
	- For downloading only the latest issue of the magazine, you can execute `poetry run fuzdownloader new`

3. The downloaded file will be defaultly saved as `{where_you_unzip_to}/Fuz-downloader-main/output/{comic_title}.pdf`.

For Language Setting:

- Execute `poetry run fuzdownloader set-lang {language code}` will change the default interface language to the specified language and run the downloader

- The following languages code are currently supported:
	- English: `en-US`
	- 繁體中文: `zh-TW`
	- 日本語: `ja-JP`

- To add or modify a language file, please fill in the format of the existing language file in `{where_you_unzip_to}/Fuz-downloader-main/data`.
	- For the case of adding language files, you should name the new language file `context-{language code}.yaml`, and write the new language code into the `list` in `language-setting.yaml`

For Output Directory Setting:

- Execute `poetry run fuzdownloader set-dir {path}` will change the default output dictionary to the path and run the downloader

- Both absolute and relative paths are acceptable.

### Using script

Useage: `fuzdownloader [Option] [Argument]`.
Try `fuz-downloader -h` or `fuz-downloader --help` for more information.


