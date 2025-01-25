# DownloadBook PDF handler

## Installation on windows

- Run the script found [here](https://gist.githubusercontent.com/JamesDawson/4d90e7fcc535c582c617ed553feaf35d/raw/333e24e5dcec3e3c9b9331c8a7273d875cc7b761/setup-pyenv-poetry-windows.ps1) in a PowerShell window. This will install python and poetry. When prompted for a version, put 3.12.
- In a terminal window visit the directory of the git checkout containing this README. Run the command `poetry install`.
- Run the command `poetry run playwright install`.
- Edit the `.env` file in the same directory for your needs.

## Minimal .env file contents

The env file must contain at least the following. Adjust to the needs of your wiki:

```
WIKI_API_URL=https://en.wikipedia.org/w/api.php
URL_PREFIX=https://en.wikipedia.org/wiki/
COLLECTION_TITLE=A Book
WIKI_BOOK_PAGE=User:hexmode
```

`COLLECTION_TITLE` will be used to name the PDF, so make sure all characters in it can be used in a filename. For example, Windows does not allow colons (“:”) so don't use them in the title if you are on Windows.

## Producing a PDF

Once you have your `.env` file set up correctly, you can create a PDF. In the terminal window, run `poetry run print_mw_collection`. Assuming you used the `.env` file above, you'll have a filo

```
poetry run render_pdf
```

## Create a binary

```
poetry self add poetry-pyinstaller-plugin
poetry install
PLAYWRIGHT_BROWSERS_PATH=0 poetry run playwright install chromium-headless-shell
poetry build --format pyinstaller
```
