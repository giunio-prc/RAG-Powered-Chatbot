from app.interfaces.agent import AIAgentInterface


class FakeAgent(AIAgentInterface):
    async def query_with_context(self, question: str, context: str) -> str:
        return (
            f'You asked me the following question:\n "{question}" \n'
            f'With the following context "{context}"\n'
            f"Unfortunately I am a fake agent I am not able to answer you"
        )
