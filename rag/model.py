from langchain.prompts import ChatPromptTemplate
from datetime import date
from openai import OpenAI

from .settings import SETTINGS

class AiModel():
    def __init__(self):
        self.client = OpenAI()
        self.prompt_template = ChatPromptTemplate.from_template(SETTINGS.get('PROMPT_TEMPLATE'))
        self.last_prompt = None

    def ask(self, question:str, context:str):
        self.last_prompt = self.prompt_template.format(question=question, context=context)

        return self.client.chat.completions.create(
            model=SETTINGS.get('GPT_MODEL'),
            messages=[
                {'role': 'system', 'content': SETTINGS.get('SYSTEM_INSTRUCTION')},
                {'role': 'user', 'content': self.last_prompt}
            ]
        ).choices[0].message.content
    