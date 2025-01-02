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

## 2024-11-10

## next

- [ ] fix bug with incorrect call of chapgpt futures queue

- [ ] add tests for main functions
- [ ] compare by sentence (to see the difference between chapters?)

- [ ] combile chapters by words (2000) into 1 file

## What is ready

- [x] make a number + chapter + filename in snake case
- [x] take a text 2000 symbols - process with open ai
- [x]return to folder formatted/ with the same filename

- [x] refactor function to one place
- [x] process all txt files in the folder
- [x] CLI
