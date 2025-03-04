import asyncio
import json
import os
from typing import List

from anthropic import AsyncAnthropic

from app.config import settings
from app.models.schemas import ShoppingItem


class LLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncAnthropic(
            api_key=settings.LLM_API_KEY,
        )

    async def _send_llm_message(self, prompt: str) -> str:
        response = await self.client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="claude-3-5-haiku-latest",
        )

        return response.content[0].text

    async def parse_shopping_list(self, text: str) -> List[ShoppingItem]:
        """
        Parse unstructured text into structured shopping items using LLM
        """

        prompt = f"""
        <Instruction>
        You are responsible for parsing a shopping list in natural
        language to JSON format following the example below. Provide always correct
        JSON strings as output. Only return the JSON as response, do not include
        any other explanation or information.
        </Instruction>

        <Example>
        <Input>Comprar espessante, luvas e fraldas</Input>
        <Output>
            [{{
                "name": fralda,
                "quantity": 1
            }},
            {{
                "name": espessante,
                "quantity": 1
            }},
            {{
                "name": luvas,
                "quantity": 1
            }}]
        </Output>
        </Example>
        <Message> {text} </Message>
        """

        message = await self._send_llm_message(prompt)

        parsed_message = json.loads(message)

        return [
            ShoppingItem(name=item["name"], quantity=item["quantity"])
            for item in parsed_message
        ]
