from asyncio import sleep
from collections.abc import AsyncGenerator
from random import random

from app.ports.agent import AIAgentInterface


class FakeAgent(AIAgentInterface):
    async def query_with_context(self, question: str, context: str) -> str:
        context_part = (
            f"With the following context: \n{context}\n"
            if context
            else "without any context\n"
        )
        return (
            f'You asked me the following question:\n "{question}" \n'
            f"{context_part}"
            "Unfortunately I am a fake agent I am not able to answer you"
        )

    async def get_stream_response(
        self, question: str, context: str
    ) -> AsyncGenerator[str, None]:
        response = await self.query_with_context(question, context)
        for word in response.split(" "):
            await sleep(0.01 * random())
            yield word + " "
