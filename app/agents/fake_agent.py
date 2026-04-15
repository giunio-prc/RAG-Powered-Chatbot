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
        word_sleep = 0.01

        phrases = [
            "You asked me the following question:\n",
            f'"{question}" \n',
            f'With the following context "{context}"\n',
            "Unfortunately I am a fake agent I am not able to answer you",
        ]

        for phrase in phrases:
            for word in phrase.split(" "):
                await sleep(word_sleep * random())
                yield word + " "
