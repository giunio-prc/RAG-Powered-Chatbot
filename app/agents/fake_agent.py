from collections.abc import AsyncIterator

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

        yield "You asked me the following question:\n"

        yield f'"{question}" \n'

        yield f'With the following context "{context}"\n'

        yield "Unfortunately I am a fake agent I am not able to answer you"
