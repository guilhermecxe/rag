from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import openai

from .settings import Settings

class AiModel():
    def __init__(self, settings:Settings):
        self._settings = settings
        self._client = self.__initialize_client(self._settings.get('OPENAI_API_KEY'))
        self._prompt_template = ChatPromptTemplate.from_template(self._settings.get('PROMPT_TEMPLATE'))

    def __initialize_client(self, api_key=None):
        return ChatOpenAI(api_key=api_key if api_key else self._settings.get('OPENAI_API_KEY'))

    def reset_client(self, api_key=None):
        """
        Reinitializes the OpenAI client.
        Can be used to apply changes on attributes used to initialize it
        on __initialize_client method.
        """
        self._client = self.__initialize_client(api_key)

    def get_client_model(self):
        return self._client

    def update_openai_api_key(self, api_key):
        if self.check_api_key(api_key):
            self.reset_client(api_key)
            return True
        else:
            return False

    def check_api_key(self, api_key=None):
        if api_key == '':
            return False
        try:
            openai.OpenAI(api_key=api_key).models.list()
        except openai.AuthenticationError:
            return False
        else:
            return True
        
    def check_model(self, model):
        """
        Checks if the model exist for OpenAI's API.
        """
        models = openai.OpenAI(api_key=self._settings.get('OPENAI_API_KEY')).models.list()
        if list(filter(lambda m: m.id == model, models)):
            return True
        else:
            return False
        
    def is_suitable_model(self, model=None):
        """
        Checks if the model works as an AI text agent.
        """
        if not model:
            model = self._settings.get('GPT_MODEL')
        
        try:
            self._client.client.create(model=model, messages=[{'role': 'user', 'content': 'Hi!'}])
        except (openai.NotFoundError, openai.PermissionDeniedError):
            return False
        else:
            return True
        
    def ask(self, question:str, context:str):
        query = self._prompt_template.format(question=question, context=context)

        return self._client.client.create(
            model=self._settings.get('GPT_MODEL'),
            messages=[
                {'role': 'system', 'content': self._settings.get('SYSTEM_INSTRUCTION')},
                {'role': 'user', 'content': query}
            ]
        ).choices[0].message.content
    