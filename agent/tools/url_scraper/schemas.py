from pydantic import BaseModel, Field
from typing import Annotated

class UrlScraperInput(BaseModel):
    url: Annotated[
        str, 
        Field(
            description="The full URL of the webpage to scrape and convert to Markdown.",
            examples=["https://www.example.com", "https://dof.gob.mx/nota_detalle.php?codigo=5777376"]
        )
    ]

class UrlScraperOutput(BaseModel):
    content: Annotated[
        str,
        Field(
            description="The content of the webpage converted to Markdown."
        )
    ]
    url: Annotated[
        str,
        Field(
            description="The URL that was scraped."
        )
    ]
    status: Annotated[
        str,
        Field(
            description="Processing status, e.g., 'success' or an error message."
        )
    ]
