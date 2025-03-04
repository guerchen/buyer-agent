from enum import Enum
from typing import List

from pydantic import BaseModel


class ShoppingItem(BaseModel):
    name: str
    quantity: int
    specifications: dict | None = None


class ShoppingList(BaseModel):
    items: List[ShoppingItem]
    user_id: str


class ProductResult(BaseModel):
    product_id: str
    name: str
    price: float
    url: str
    description: str


class PurchaseConfirmation(BaseModel):
    items: List[str]  # List of product_ids
    user_id: str


class ChatMessage(BaseModel):
    user_id: str
    message: str
    timestamp: str
    is_bot: bool = False


class ConversationState(Enum):
    INITIAL = "initial"
    ITEMS_FOUND = "items_found"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    PURCHASE_AUTHORIZED = "purchase_authorized"


class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state = ConversationState.INITIAL
        self.current_items = []
        self.found_products = []
        self.selected_products = []
