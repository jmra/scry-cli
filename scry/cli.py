import sys

import click
import requests

from .api import ScryfallClient
from .display import render_card, render_search_results
from .models import Card

MAX_PAGES = 10


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, requests.HTTPError):
        try:
            msg = exc.response.json().get("details", str(exc))
        except Exception:
            msg = str(exc)
    elif isinstance(exc, requests.ConnectionError):
        msg = "Could not connect to Scryfall. Check your network connection."
    elif isinstance(exc, requests.Timeout):
        msg = "Request timed out."
    else:
        msg = str(exc)
    click.echo(click.style(f"Error: {msg}", fg="red"), err=True)
    sys.exit(1)


@click.group()
def cli() -> None:
    """Query the Scryfall Magic: The Gathering API."""


@cli.command()
@click.argument("name", nargs=-1, required=True)
@click.option("--exact", is_flag=True, default=False, help="Use exact name match.")
@click.option("--plain", is_flag=True, default=False, help="Plain text output.")
def named(name: tuple[str, ...], exact: bool, plain: bool) -> None:
    """Look up a card by name. Fuzzy match by default.

    \b
    Examples:
      scry named lightning bolt
      scry named --exact "Lightning Bolt"
    """
    client = ScryfallClient()
    try:
        data = client.card_named(" ".join(name), exact=exact)
    except Exception as exc:
        _handle_error(exc)
    render_card(Card.from_api(data), plain=plain)


@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--page", default=1, show_default=True, help="Page number.")
@click.option("--all", "fetch_all", is_flag=True, default=False, help="Fetch all pages.")
@click.option("--plain", is_flag=True, default=False, help="Plain text output.")
def search(query: tuple[str, ...], page: int, fetch_all: bool, plain: bool) -> None:
    """Search for cards using a Scryfall query string.

    \b
    Examples:
      scry search t:creature c:red cmc=1
      scry search "e:mh3 r:mythic" --page 2
      scry search t:dragon --all
    """
    client = ScryfallClient()
    q = " ".join(query)
    try:
        if fetch_all:
            all_cards: list[Card] = []
            current_page = 1
            total = 0
            while current_page <= MAX_PAGES:
                result = client.card_search(q, page=current_page)
                total = result.get("total_cards", 0)
                all_cards.extend(Card.from_api(c) for c in result["data"])
                if not result.get("has_more"):
                    break
                current_page += 1
            else:
                click.echo(
                    click.style(
                        f"Warning: stopped after {MAX_PAGES} pages. Use --page to fetch more.",
                        fg="yellow",
                    ),
                    err=True,
                )
            render_search_results(all_cards, total, plain=plain)
        else:
            result = client.card_search(q, page=page)
            cards = [Card.from_api(c) for c in result["data"]]
            total = result.get("total_cards", len(cards))
            render_search_results(cards, total, plain=plain)
            if result.get("has_more"):
                click.echo(
                    click.style(
                        f"More results available. Use --page {page + 1} or --all.",
                        fg="cyan",
                    )
                )
    except Exception as exc:
        _handle_error(exc)


@cli.command()
def syntax() -> None:
    """Show a reference of Scryfall query syntax keywords."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box

        console = Console()

        def section(title: str, rows: list[tuple[str, str, str]]) -> None:
            t = Table(title=title, box=box.SIMPLE, show_header=True, header_style="bold")
            t.add_column("Keyword", style="bold cyan", no_wrap=True)
            t.add_column("Example", style="green", no_wrap=True)
            t.add_column("Description")
            for kw, ex, desc in rows:
                t.add_row(kw, ex, desc)
            console.print(t)

        section("Card Name & Text", [
            ("name:", 'name:"bolt"', "Card name contains word (default field, quotes optional)"),
            ("o:", "o:flying", "Oracle text contains word"),
            ("o:", 'o:"first strike"', "Oracle text contains exact phrase"),
            ("keyword:", "keyword:deathtouch", "Card has keyword ability"),
        ])
        section("Types", [
            ("t:", "t:creature", "Type line contains word (type, subtype, or supertype)"),
            ("t:", "t:legendary", "Supertype filter"),
            ("t:", "t:goblin", "Subtype filter"),
            ("t:", "t:artifact t:creature", "Multiple types (AND)"),
        ])
        section("Colors & Mana", [
            ("c:", "c:red", "Color (white/blue/black/red/green or w/u/b/r/g)"),
            ("c:", "c:wu", "Exactly white and blue (no other colors)"),
            ("c>=", "c>=wu", "At least white and blue"),
            ("c:", "c:m", "Multicolor cards"),
            ("c:", "c:c", "Colorless cards"),
            ("id:", "id:gruul", "Color identity (for Commander)"),
            ("m:", "m:{2}{R}", "Exact mana cost"),
            ("cmc:", "cmc=3", "Converted mana cost (also <=, >=, <, >)"),
        ])
        section("Power, Toughness & Loyalty", [
            ("pow:", "pow>=4", "Power comparison"),
            ("tou:", "tou<=2", "Toughness comparison"),
            ("loy:", "loy=3", "Starting loyalty"),
        ])
        section("Sets & Rarity", [
            ("e:", "e:mh3", "Set by code (edition)"),
            ("r:", "r:mythic", "Rarity: common / uncommon / rare / mythic"),
            ("cn:", "cn=42", "Collector number"),
            ("lang:", "lang:ja", "Language code"),
        ])
        section("Format Legality", [
            ("f:", "f:standard", "Legal in format"),
            ("f:", "f:commander", "Legal in Commander"),
            ("banned:", "banned:legacy", "Banned in format"),
            ("restricted:", "restricted:vintage", "Restricted in format"),
        ])
        section("Prices", [
            ("usd:", "usd<=1", "Price in USD (TCGPlayer)"),
            ("usd:", "usd>=10", "Expensive cards"),
            ("eur:", "eur<5", "Price in EUR (Cardmarket)"),
        ])
        section("Boolean Operators", [
            ("AND", "t:elf AND c:g", "Both conditions must match (default between terms)"),
            ("OR", "t:goblin OR t:orc", "Either condition"),
            ("NOT / -", "-t:creature", "Exclude matches"),
            ("()", "(c:r OR c:g) t:instant", "Grouping"),
        ])
        section("Other Useful Keywords", [
            ("a:", "a:terese-nielsen", "Artist name (hyphenated)"),
            ("year:", "year=1993", "Year printed"),
            ("is:", "is:firstprint", "Flags: firstprint, reprint, dual, fetchland, etc."),
            ("has:", "has:watermark", "Has property: watermark, flavor, etc."),
            ("game:", "game:paper", "Available in: paper, mtgo, arena"),
        ])

        console.print(
            "[dim]Full syntax reference: https://scryfall.com/docs/syntax[/]"
        )

    except ImportError:
        lines = [
            "SCRYFALL QUERY SYNTAX REFERENCE",
            "",
            "CARD NAME & TEXT",
            '  name:     name:"bolt"          Card name contains word',
            "  o:        o:flying              Oracle text contains word",
            "  keyword:  keyword:deathtouch    Card has keyword ability",
            "",
            "TYPES",
            "  t:        t:creature            Type, subtype, or supertype",
            "  t:        t:legendary t:goblin  Multiple types (AND)",
            "",
            "COLORS & MANA",
            "  c:        c:red                 Color (or w/u/b/r/g)",
            "  c:        c:wu                  Exactly white+blue",
            "  c>=       c>=wu                 At least white+blue",
            "  c:        c:m / c:c             Multicolor / Colorless",
            "  id:       id:gruul              Color identity",
            "  cmc:      cmc=3                 Mana value (also <=, >=)",
            "",
            "SETS & RARITY",
            "  e:        e:mh3                 Set code",
            "  r:        r:mythic              common/uncommon/rare/mythic",
            "",
            "FORMAT",
            "  f:        f:standard            Legal in format",
            "  f:        f:commander           Legal in Commander",
            "",
            "PRICES",
            "  usd:      usd<=1               Price in USD",
            "",
            "OPERATORS",
            "  AND OR NOT -  (t:goblin OR t:orc) -r:common",
            "",
            "Full reference: https://scryfall.com/docs/syntax",
        ]
        click.echo("\n".join(lines))


@cli.command("random")
@click.option("--query", "-q", default=None, help="Filter by a Scryfall query.")
@click.option("--plain", is_flag=True, default=False, help="Plain text output.")
def random_card(query: str | None, plain: bool) -> None:
    """Fetch a random card, optionally filtered by a query.

    \b
    Examples:
      scry random
      scry random --query t:dragon
    """
    client = ScryfallClient()
    try:
        data = client.card_random(query=query)
    except Exception as exc:
        _handle_error(exc)
    render_card(Card.from_api(data), plain=plain)
