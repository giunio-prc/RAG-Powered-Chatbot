import logging

from dotenv import load_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import StrOutputParser
from langchain_cohere import ChatCohere
from langchain_core.runnables import RunnableSequence

from app.interfaces.agent import AIAgentInterface

load_dotenv()


logger = logging.getLogger("uvicorn")


class CohereAgent(AIAgentInterface):
    chain: RunnableSequence

    def __init__(self):
        self.model = ChatCohere(model="command-r-plus")
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.prompt_template
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            template="{question}"
        )
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        self.chain = chat_prompt_template | self.model | StrOutputParser()

    async def query_with_context(self, question: str, context: str) -> str:
        logger.debug(f"Question: {question}")
        logger.debug(f"Context: {context}")
        response = await self.chain.ainvoke({"question": question, "context": context})
        return response
