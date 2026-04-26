import click

from .models import Card

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

RARITY_COLORS = {
    "common": "white",
    "uncommon": "bright_white",
    "rare": "yellow",
    "mythic": "bright_red",
}


def render_card(card: Card, plain: bool = False) -> None:
    if plain or not HAS_RICH:
        _render_plain(card)
    else:
        _render_rich(card)


def render_search_results(cards: list[Card], total: int, plain: bool = False) -> None:
    if plain or not HAS_RICH:
        click.echo(f"Showing {len(cards)} of {total} results\n")
    else:
        console.print(f"[dim]Showing {len(cards)} of {total} results[/]\n")
    for card in cards:
        render_card(card, plain=plain)


def _render_rich(card: Card) -> None:
    color = RARITY_COLORS.get(card.rarity, "white")

    body = Text()
    if card.mana_cost:
        body.append(card.mana_cost + "   ", style="bold cyan")
    body.append(card.type_line + "\n", style="italic")
    body.append(
        f"Rarity: {card.rarity.title()}   Set: {card.set_code} ({card.set_name})\n",
        style="dim",
    )
    body.append("\n")
    body.append(card.oracle_text)
    if card.power is not None:
        body.append(f"\n\nP/T: {card.power}/{card.toughness}", style="bold")

    panel = Panel(body, title=f"[bold {color}]{card.name}[/]", expand=False)
    console.print(panel)


def _render_plain(card: Card) -> None:
    click.echo(click.style(card.name, bold=True))
    parts = []
    if card.mana_cost:
        parts.append(card.mana_cost)
    parts.append(card.type_line)
    click.echo("  " + "   ".join(parts))
    click.echo(f"  {card.rarity.title()} — {card.set_code} ({card.set_name})")
    click.echo()
    for line in card.oracle_text.splitlines():
        click.echo(f"  {line}")
    if card.power is not None:
        click.echo(f"\n  P/T: {card.power}/{card.toughness}")
    click.echo()
