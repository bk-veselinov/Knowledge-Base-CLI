from functools import wraps

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from knowledge.cli_types import (
    DEFAULT_LIMIT,
    ItemContent,
    ItemId,
    ItemTitle,
    LimitOption,
    Query,
)
from knowledge.config import get_database_path
from knowledge.errors import InvalidInputError, KnowledgeError
from knowledge.manager import KnowledgeManager
from knowledge.models import KnowledgeItem
from knowledge.repository import SqliteRepository

app = typer.Typer(help="A CLI for managing knowledge items.")
console = Console()
error_console = Console(stderr=True)


def _handle_knowledge_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except InvalidInputError as e:
            error_console.print(f"Error: {e}", style="red")
            raise typer.Exit(code=2)
        
        except KnowledgeError as e:
            error_console.print(f"Error: {e}", style="red")
            raise typer.Exit(code=1)
        
    return wrapper

@app.command("add", help="Add a new knowledge item.")
@_handle_knowledge_error
def add_item(
    title: ItemTitle,
    content: ItemContent
) -> None:
    """Add a new knowledge item."""
    manager = _knowledge_manager()
    item = manager.add_item(title, content)
    console.print(f"Added item: {item.title} (ID: {item.id})")

@app.command("show", help="Get a knowledge item by ID.")
@_handle_knowledge_error
def get_item(
    item_id: ItemId
) -> None:
    """Get a knowledge item by ID."""
    manager = _knowledge_manager()
    item = manager.get_item(item_id)
    console.print(f"Title: {item.title}\nCreated at: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\nContent:\n{item.content}")


@app.command("search", help="Search for knowledge items.")
@_handle_knowledge_error
def search_items(
    query: Query,
    limit: LimitOption = DEFAULT_LIMIT
) -> None:
    """Search for knowledge items."""

    manager = _knowledge_manager()
    filtered_items = manager.search_items(query, limit)
    if not filtered_items:
        console.print(f"No knowledge items found matching '{query}'.")
        return
    
    table = _create_list_table([item.knowledge_item for item in filtered_items])
    table.add_column("Score", justify="right")
    table.columns[-1]._cells.extend([f"{item.score:.2f}" for item in filtered_items])
        
    console.print(table)

@app.command("list", help="List all knowledge items.")
@_handle_knowledge_error
def list_items(
    limit: LimitOption = None
) -> None:
    """List all knowledge items."""
    manager = _knowledge_manager()
    items = manager.list_items()

    if not items:
        typer.echo("No knowledge items found.")
        return

    if limit is None:
        limit = len(items)

    table = _create_list_table(items[:limit])
    console.print(table)

@app.command("delete", help="Delete a knowledge item by ID.")
@_handle_knowledge_error
def delete_item(
    item_id: ItemId
) -> None:
    """Delete a knowledge item by ID."""
    manager = _knowledge_manager()
    deleted_item = manager.delete_item(item_id)
    console.print(f"Deleted item: {deleted_item.title} (ID: {deleted_item.id})")

def main() -> None:
    """Entry point for the CLI."""
    load_dotenv()
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
        table.add_row(str(item.id), item.title, str(item.created_at.strftime('%Y-%m-%d %H:%M:%S')))

    return table

