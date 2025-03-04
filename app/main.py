import json

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.schemas import ConversationState, PurchaseConfirmation, ShoppingList
from app.services.cart_service import CartService
from app.services.llm_service import LLMService
from app.services.store_service import StoreService
from app.utils.connection_manager import ConnectionManager

app = FastAPI(title="Buyer Agent API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize services
llm_service = LLMService(settings.LLM_API_KEY)
store_service = StoreService(settings.STORE_BASE_URL)
cart_service = CartService()
manager = ConnectionManager()


# HTML chat interface endpoint
@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            session = manager.user_sessions[user_id]

            if session.state == ConversationState.INITIAL:
                # Parse the initial shopping list
                items = await llm_service.parse_shopping_list(message_data["message"])
                session.current_items = items

                # Search for products
                results = []
                for item in items:
                    products = await store_service.search_products(item)
                    results.extend(products)
                session.found_products = results

                # Format response with numbered options
                response = "I found these items. Please select the ones you want by typing their numbers (e.g., '1, 3, 4'):\n\n"
                for idx, result in enumerate(results, 1):
                    response += f"{idx}. {result.name}: ${result.price}\n"

                session.state = ConversationState.ITEMS_FOUND
                await manager.send_message(response, user_id)

            elif session.state == ConversationState.ITEMS_FOUND:
                try:
                    # Parse selected item numbers
                    selected_indices = [
                        int(idx.strip()) - 1
                        for idx in message_data["message"].split(",")
                    ]
                    selected_products = [
                        session.found_products[idx] for idx in selected_indices
                    ]
                    session.selected_products = selected_products

                    # Calculate total and ask for confirmation
                    total = sum(product.price for product in selected_products)
                    response = (
                        f"Your selected items total: ${total:.2f}\n\n"
                        "Selected items:\n"
                        + "\n".join(
                            f"- {product.name}: ${product.price}"
                            for product in selected_products
                        )
                        + "\n\nType 'confirm' to proceed with the purchase or 'cancel' to start over."
                    )

                    session.state = ConversationState.AWAITING_CONFIRMATION
                    await manager.send_message(response, user_id)

                except (ValueError, IndexError):
                    await manager.send_message(
                        "Invalid selection. Please use numbers separated by commas (e.g., '1, 3, 4').",
                        user_id,
                    )

            elif session.state == ConversationState.AWAITING_CONFIRMATION:
                decision = message_data["message"].lower().strip()

                if decision == "confirm":
                    # Process the purchase
                    product_ids = [
                        product.product_id for product in session.selected_products
                    ]
                    success = await store_service.purchase_products(product_ids)

                    if success:
                        response = "Purchase completed successfully! Would you like to buy anything else?"
                    else:
                        response = "There was an error processing your purchase. Please try again."

                    session.state = ConversationState.INITIAL
                    session.current_items = []
                    session.found_products = []
                    session.selected_products = []

                elif decision == "cancel":
                    response = "Purchase cancelled. What would you like to buy?"
                    session.state = ConversationState.INITIAL
                    session.current_items = []
                    session.found_products = []
                    session.selected_products = []

                else:
                    response = "Please type 'confirm' to proceed with the purchase or 'cancel' to start over."

                await manager.send_message(response, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
