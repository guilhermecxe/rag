from langchain.prompts import ChatPromptTemplate
import openai

from .settings import SETTINGS

class AiModel():
    def __init__(self):
        self.client = openai.OpenAI()
        self.prompt_template = ChatPromptTemplate.from_template(SETTINGS.get('PROMPT_TEMPLATE'))
        self.last_prompt = None

    def reset_client(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key)

    def update_openai_api_key(self, api_key):
        if self.check_api_key(api_key):
            self.reset_client(api_key)
            return True
        else:
            return False

    def check_api_key(self, api_key=None):
        new_client = openai.OpenAI(api_key=api_key)
        try:
            new_client.models.list()
        except openai.AuthenticationError:
            return False
        else:
            return True
        
    def check_model(self, model):
        models = self.client.models.list()
        if list(filter(lambda m: m.id == model, models)):
            return True
        else:
            return False

    def ask(self, question:str, context:str):
        self.last_prompt = self.prompt_template.format(question=question, context=context)

        return self.client.chat.completions.create(
            model=SETTINGS.get('GPT_MODEL'),
            messages=[
                {'role': 'system', 'content': SETTINGS.get('SYSTEM_INSTRUCTION')},
                {'role': 'user', 'content': self.last_prompt}
            ]
        ).choices[0].message.content
    