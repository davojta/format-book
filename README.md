# format-book

set of utils to format books in different formats

## getting started

```bash
pipx install poetry
```

See also poetry docs)[https://python-poetry.org/docs/]

### run script

```bash
poetry run python main.py generate-stats --help
```

### install dependencies

```bash
poetry install
```

## What is the next

## next


- [ ] add logger
- [ ] compare by sentence (to see the difference between chapters?)
- [ ] add cli to extract text from epub
- [ ] add cli to extract text from pdf
- [ ] run prompt to get simple finnish text from normal text
- [ ] run prompt to get anki csv from the text file
- [ ] add algorithmic way to remove garbage in the text - trailing whitespaces and repeated new lines
- [ ] process pikku prinssi book
- [ ] process language folders book (format chapters)
- [ ] extract from docx (export from the google)
- [ ] process tonttu (folders inside folders, docx, ignore images)
- [ ] process Toinen vuosi Malory Towersissa (epub)


## What is ready

## 2025-01-18

- [x] add github actions
- [x] combile chapters by words (2000) into 1 file

## initial
- [x] add dotenv
- [x] add tests for format_book functions

- [x] fix bug with incorrect call of chapgpt futures queue

- [x] make a number + chapter + filename in snake case
- [x] take a text 2000 symbols - process with open ai
- [x] return to folder formatted/ with the same filename

- [x] refactor function to one place
- [x] process all txt files in the folder
- [x] CLI
