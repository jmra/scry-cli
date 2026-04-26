# scry-cli

A Python CLI tool for querying the [Scryfall](https://scryfall.com) API for Magic: The Gathering card data.
Made using Claude Code, Sonnet 4.6

## Project Structure

```
scry-cli/
├── pyproject.toml       # Project config, dependencies, entry point
└── scry/
    ├── __init__.py      # Version string
    ├── api.py           # Scryfall HTTP client + rate limiter
    ├── models.py        # Card dataclass
    ├── display.py       # Terminal rendering (rich + plain fallback)
    └── cli.py           # Click CLI commands
```

## Installation

```bash
pip install -e . --no-build-isolation
```

Installs the `scry` console script.

## Commands

| Command | Description |
|---|---|
| `scry named <name...>` | Look up a card by name (fuzzy match by default) |
| `scry search <query...>` | Search using Scryfall query syntax |
| `scry random` | Fetch a random card |
| `scry syntax` | Show a query syntax reference |

### Options

**`scry named`**
- `--exact` — use exact name match instead of fuzzy
- `--plain` — plain text output (no rich formatting)

**`scry search`**
- `--page N` — fetch a specific results page
- `--all` — fetch all pages (capped at 10)
- `--plain` — plain text output

**`scry random`**
- `--query / -q` — filter the random pool with a Scryfall query
- `--plain` — plain text output

## Dependencies

- `click>=8.0` — CLI framework
- `requests>=2.25` — HTTP client
- `rich>=13.0` — terminal rendering