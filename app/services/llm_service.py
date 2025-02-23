from typing import List
from app.models.schemas import ShoppingItem


class LLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def parse_shopping_list(self, text: str) -> List[ShoppingItem]:
        """
        Parse unstructured text into structured shopping items using LLM
        """
        # Implement LLM call to structure the text
        pass
