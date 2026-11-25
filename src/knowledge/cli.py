
import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from knowledge.config import get_database_path
from knowledge.errors import KnowledgeError
from knowledge.manager import KnowledgeManager
from knowledge.models import KnowledgeItem
from knowledge.repository import SqliteRepository
from knowledge.cli_types import ItemId, ItemTitle, ItemContent, Query, LimitOption



app = typer.Typer(help="A CLI for managing knowledge items.")

@app.command("add", help="Add a new knowledge item.")
def add_item(
    title: ItemTitle,
    content: ItemContent
):
    """Add a new knowledge item."""
    manager = _knowledge_manager()
    item = manager.add_item(title, content)
    typer.echo(f"Added item: {item.title} (ID: {item.id})")

@app.command("show", help="Get a knowledge item by ID.")
def get_item(
    item_id: ItemId
):
    """Get a knowledge item by ID."""
    try:
        manager = _knowledge_manager()
        item = manager.get_item(item_id)
        typer.echo(f"Title: {item.title}\nCreated at: {item.created_at}\n\nContent: {item.content}")
    except KnowledgeError as e:
        typer.echo(f"Error: {e}", err=True)


@app.command("search", help="Search for knowledge items.")
def search_items(
    query: Query,
    limit: LimitOption
) -> None:
    """Search for knowledge items."""
    manager = _knowledge_manager()
    items = manager.list_items()

    query = query.strip().casefold()

    if not query:
        typer.echo("Query cannot be empty.", err=True)
        return

    if items is None:
        typer.echo("No knowledge items found.")
        return

    filtered_items = [item for item in items 
                      if query in item.title.casefold() 
                        or query in item.content.casefold()]

    if not filtered_items:
        typer.echo(f"No knowledge items found matching the query: '{query}'")
        return

    table = _create_list_table(filtered_items[:limit])
    console = Console()
    console.print(table)

@app.command("list", help="List all knowledge items.")
def list_items(
    limit: LimitOption
) -> None:
    """List all knowledge items."""
    manager = _knowledge_manager()
    items = manager.list_items()

    if items is None:
        typer.echo("No knowledge items found.")
        return

    table = _create_list_table(items[:limit])
    console = Console()
    console.print(table)

@app.command("delete", help="Delete a knowledge item by ID.")
def delete_item(
    item_id: ItemId
) -> None:
    """Delete a knowledge item by ID."""
    try:
        manager = _knowledge_manager()
        deleted_item = manager.delete_item(item_id)
        typer.echo(f"Deleted item: {deleted_item.title} (ID: {deleted_item.id})")
    except KnowledgeError as e:
        typer.echo(f"Error: {e}", err=True)

def main() -> None:
    """Entry point for the CLI."""
    app()

def _knowledge_manager() -> KnowledgeManager:
    """Create and return a KnowledgeManager instance."""
    return KnowledgeManager(SqliteRepository(get_database_path()))

def _create_list_table(knowledge_items: list[KnowledgeItem]) -> Table:
    """Create the knowledge_items table"""
    table = Table(title="Knowledge Items")
    table.add_column("ID", justify="right", no_wrap=True)
    table.add_column("Title")
    table.add_column("Created at", justify="right")

    for item in knowledge_items:
        table.add_row(str(item.id), item.title, str(item.created_at))

    return table