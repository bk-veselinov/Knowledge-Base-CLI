# Knowledge Base CLI

A command-line tool for storing short notes (title + content) and finding them with relevance-ranked search.

## Setup

Requires Python 3.11+.

```bash
git clone https://github.com/bk-veselinov/Knowledge-Base-CLI

python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
source .venv/bin/activate         # macOS / Linux
pip install -e ".[dev]"
```

The database is stored at `~/knowledge/knowledge.db` by default. To change it, set `DB_PATH` in `.env`.

## Usage

```bash
knowledge add "Python" "Python is a high-level programming language."
knowledge list [--limit N]
knowledge show 1
knowledge search "python async" [--limit N]
knowledge delete 1
```

`python -m knowledge <command>` works too. Exit codes: `0` success, `1` not found / storage error, `2` invalid input.

## Tests

```bash
pytest
```

- `test_repository.py`: SQLite storage, on a temporary database
- `test_manager.py`: validation and search, on a temporary database
- `test_cli.py`: output and exit codes, with a mocked manager

## Design decisions

**Architecture.** `cli.py` (Typer) handles parsing, output and exit codes only. `manager.py` holds the validation rules. `repository.py` handles storage, and `improved_search.py` is a pure ranking function. Errors are `KnowledgeError` subclasses, turned into messages in one CLI decorator, so users never see a stack trace.

**Storage: SQLite.** It's in the standard library and keeps everything in one file. Writes are transactional, so an interrupted command can't corrupt the data.

**Optional feature: ranked search.** Text is casefolded (works for Cyrillic) and split into words and matched by prefix, ignoring punctuation and common EN/BG stopwords. Each query word scores `3.5` for a title match plus `log(1 + n)` for `n` content matches. The total is scaled by the share of query words matched, squared, and words appearing in order as a phrase add a bonus. The weights are constants in `improved_search.py`.

**Assumptions.** Single local user. Small collections. Timestamps are stored in UTC. A query of only stopwords is rejected.

**Use of AI tools.** I used Claude Code to review the search logic and weights and to validate some design decesions. It found bugs such as content frequency always being 1 and a division by zero on stopword-only queries. I decided which suggestions to apply, and checked every change with the test suite and by running the CLI. The `README.md` file was written by AI and then edited by me.
