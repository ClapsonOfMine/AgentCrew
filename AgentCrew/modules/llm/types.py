from pydantic import BaseModel
from typing import List, Literal


class Model(BaseModel):
    """Model metadata class."""

    id: str
    provider: str
    name: str
    description: str
    capabilities: List[str]
    default: bool = False
    input_token_price_1m: float = 0.0
    output_token_price_1m: float = 0.0
    endpoint: Literal["completions", "response"] = "completions"
