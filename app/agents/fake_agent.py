from asyncio import sleep
from collections.abc import AsyncIterator
from random import random

from app.interfaces.agent import AIAgentInterface


class FakeAgent(AIAgentInterface):

    async def query_with_context(self, question: str, context: str) -> str:
        return (
            f'You asked me the following question:\n "{question}" \n'
            f'With the following context "{context}"\n'
            "Unfortunately I am a fake agent I am not able to answer you"
        )

    async def get_stream_response(
        self, question: str, context: str
        ) -> AsyncIterator[str]:

        char_sleep = 5.0 / len(f"{context}{question}")
        phrase_sleep = char_sleep * 2

        for char in "You asked me the following question:\n":
            await sleep(char_sleep * random())
            yield char

        await sleep(phrase_sleep * random())

        for char in f'"{question}" \n':
            await sleep(char_sleep * random())
            yield char

        await sleep(phrase_sleep * random())


        for char in f'With the following context "{context}"\n':
            await sleep(char_sleep * random())
            yield char

        await sleep(phrase_sleep * random())

        for char in "Unfortunately I am a fake agent I am not able to answer you":
            await sleep(char_sleep * random())
            yield char
