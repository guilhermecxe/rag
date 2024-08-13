from langchain.prompts import ChatPromptTemplate
from datetime import date
from openai import NotFoundError
import openai
import os

from .settings import SETTINGS

class AiModel():
    def __init__(self):
        self.client = openai.OpenAI()
        self.prompt_template = ChatPromptTemplate.from_template(SETTINGS.get('PROMPT_TEMPLATE'))
        self.last_prompt = None

    def reset_client(self):
        self.client = openai.OpenAI()

    def update_openai_api_key(self, api_key):
        if self.check_api_key(api_key):
            os.environ['OPENAI_API_KEY'] = api_key
            return True
        else:
            return False

    def check_api_key(self, api_key=None):
        old_key = os.environ['OPENAI_API_KEY']
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            self.reset_client()
        try:
            self.client.models.list()
        except openai.AuthenticationError:
            os.environ['OPENAI_API_KEY'] = old_key
            self.reset_client()
            return False
        else:
            os.environ['OPENAI_API_KEY'] = old_key
            self.reset_client()
            return True
        
    def check_model(self, model):
        new_client = openai.OpenAI()
        try:
            new_client.chat.completions.create(model=model, messages=[{'role': 'user', 'content': 'Hello!'}])
        except NotFoundError:
            return False
        else:
            return True

    def ask(self, question:str, context:str):
        self.last_prompt = self.prompt_template.format(question=question, context=context)

        return self.client.chat.completions.create(
            model=SETTINGS.get('GPT_MODEL'),
            messages=[
                {'role': 'system', 'content': SETTINGS.get('SYSTEM_INSTRUCTION')},
                {'role': 'user', 'content': self.last_prompt}
            ]
        ).choices[0].message.content
    