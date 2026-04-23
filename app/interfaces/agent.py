from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

template: str = """
    You are a customer support Chatbot.
    You assist users with general inquiries
    and technical issues.
    You will answer to the question:
    -----------
    {question}
    -----------
    Your answer will only be based on the knowledge
    of the context below you are trained on.
    -----------
    {context}
    -----------
    if you don't know the answer,
    you will ask the user to rephrase the question
    or redirect the user the contact@avenueit.be
    always be friendly and helpful
    at the end of the conversation.
    Only if you provide the answer
    ask the user if they are satisfied
    if yes, say goodbye and end the conversation
    """


class AIAgentInterface(ABC):
    prompt_template: str = template

    @abstractmethod
    async def query_with_context(self, question: str, context: str) -> str:
        pass

    @abstractmethod
    def get_stream_response(
        self, question: str, context: str
    ) -> AsyncGenerator[str, None]:
        pass
