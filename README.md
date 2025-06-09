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

## On your own wiki

You can run this on your own wiki. For this demonstration we'll create a book titled “21st Century Presidents” that (as of June 2025) contains the following presidents:

- George W. Bush
- Barack Obama
- Donald Trump
- Joe Biden

You will need Cite, TitleBlacklist, Scribunto, ParserFunctions, and TemplateStyles

JsonConfig needs to be installed with the configuration pointing to wikimedia commons.

Which you can download using:

```
curl 'https://en.wikipedia.org/wiki/Special:Export' \
  --compressed  -X POST -H 'User-Agent: My downloader' -o 21st_century_presidents.xml \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'title=Special%3AExport^&catname=^&pages=George+W.+Bush%0D%0ABarack+Obama%0D%0ADonald+Trump%0D%0AJoe+Biden%0D%0AMediaWiki%3ACommon.css%0D%0AMediaWiki%3APrint.css%0D%0A^&curonly=1^&templates=1^&wpDownload=1^&wpEditToken=%2B%5C'
```

And then import to your wiki using

```
$ maintenance/run importDump 21st_century_presidents.xml
  100 (50.83 pages/sec 50.83 revs/sec)
  200 (44.15 pages/sec 44.15 revs/sec)
  300 (38.57 pages/sec 38.57 revs/sec)
  400 (6.96 pages/sec 6.96 revs/sec)
  500 (3.13 pages/sec 3.13 revs/sec)
  Done!
  You might want to run rebuildrecentchanges.php to regenerate RecentChanges,
  and initSiteStats.php to update page and revision counts
$ maintenance/run rebuildrecentchanges
  Rebuilding $wgRCMaxAge=7776000 seconds (90 days)
  Clearing recentchanges table for time range...
  Loading from page and revision tables...
  Inserting from page and revision tables...
  Updating links and size differences...
  Loading from user and logging tables...
  Flagging bot account edits...
  Flagging auto-patrolled edits...
  Removing duplicate revision and logging entries...
  Deleting feed timestamps.
  Done.
$ maintenance/run initSiteStats
  Refresh Site Statistics

  Counting total edits...565
  Counting number of articles...5
  Counting total pages...564
  Counting number of users...3
  Counting number of images...0

  To update the site statistics table, run the script with the --update option.

  Done.
$
```
