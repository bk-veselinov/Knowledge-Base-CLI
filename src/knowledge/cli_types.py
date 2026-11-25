from typing import Annotated

from typer import Argument, Option


ItemId = Annotated[
    int, 
    Argument(help="The ID of the item.")
]

ItemTitle = Annotated[
    str,
    Argument(help="The title of the item.")
]

ItemContent = Annotated[
    str,
    Argument(help="The content of the item.")
]

Query = Annotated[
    str,
    Argument(help="A query string to search for in the knowledge items.")
]

LimitOption = Annotated[
    int,
    Option("--limit", "-l", help="The maximum number of items to return.", min=1, default=10)
]