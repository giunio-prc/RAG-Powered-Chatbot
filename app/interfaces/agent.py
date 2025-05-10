from abc import ABC, abstractmethod


class AIAgentInterface(ABC):
    model: object
    chat_prompt_template: object
    chain: object

    @abstractmethod
    async def query_with_context(self, question: str, context: str) -> str:
        pass
