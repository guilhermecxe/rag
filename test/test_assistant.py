import pytest
import os
from dotenv import load_dotenv
from pydantic.v1.main import ValidationError
from langchain.schema.document import Document

from rag.assistant import Assistant

class TestAssistant(object):
    @classmethod
    def setup_class(cls):
        cls.ai = Assistant()
        cls.ai.reset_contents_database()
        cls.ai.reset_chat_database()
        print('\nDEBUG: Setup method executed.')

    @classmethod
    def teardown_class(cls):
        cls.ai.reset_contents_database()
        cls.ai.reset_chat_database()
        print('\nDEBUG: Teardown method executed.')

    def test_reset_contents_database(self):
        self.ai.reset_contents_database()
        contents = self.ai.get_available_contents()
        assert len(contents) == 0

    def test_get_available_contents(self):
        content_path1 = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        content_path2 = 'sample_contents\\People.xlsx'
        self.ai.add_content(content_path1)
        self.ai.add_content(content_path2)
        available_contents = self.ai.get_available_contents()
        assert set(available_contents) == set([content_path1, content_path2])

    def test_add_content_pdf(self):
        content_path = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        self.ai.delete_contents([content_path]) # ensuring content not in the database
        self.ai.add_content(content_path)
        available_contents = self.ai.get_available_contents()
        assert content_path in available_contents

    def test_add_content_xlsx(self):
        content_path = 'sample_contents\\People.xlsx'
        self.ai.delete_contents([content_path]) # ensuring content not in the database
        self.ai.add_content(content_path)
        available_contents = self.ai.get_available_contents()
        assert content_path in available_contents

    def test_delete_contents(self):
        content_path1 = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        content_path2 = 'sample_contents\\People.xlsx'
        self.ai.add_content(content_path1)
        self.ai.add_content(content_path2)
        self.ai.delete_contents([content_path1])
        available_contents = self.ai.get_available_contents()
        assert not content_path1 in available_contents
        assert content_path2 in available_contents

    def test_check_valid_api_key(self):
        assert self.ai.check_api_key() # considering valid api key on PATH

    def test_check_invalid_api_key(self):
        assert not self.ai.check_api_key('abc')

    def test_check_valid_model(self):
        assert self.ai.check_model('gpt-4o-mini')

    def test_check_invalid_model(self):
        assert not self.ai.check_model('gpt-3k-maxi')

    def test_update_valid_settings(self):
        valid_settings = {
            'openai_api_key': os.environ['OPENAI_API_KEY'], # considering valid api key on PATH
            'gpt_model': 'gpt-4o-mini',
        }
        self.ai.update_settings(**valid_settings)
        assert self.ai._settings.get('GPT_MODEL') == valid_settings['gpt_model']
        assert self.ai._settings.get('OPENAI_API_KEY') == valid_settings['openai_api_key']

    def test_update_invalid_settings(self):
        with pytest.raises(ValueError, match='Invalid OpenAI API key'):
            self.ai.update_settings(openai_api_key='abc')
        with pytest.raises(ValueError, match='Invalid GPT Model'):
            self.ai.update_settings(gpt_model='abc')

    def test_no_api_key(self):
        current_key = self.ai._settings.get('OPENAI_API_KEY') # saving current api key
        os.environ.pop('OPENAI_API_KEY', None) # removing api key from PATH
        self.ai._settings.set('OPENAI_API_KEY', None) # ensuring no api key
        with pytest.raises(ValidationError):
            Assistant()
        self.ai.update_settings(openai_api_key=current_key) # returning to the initial configuration
        load_dotenv('.env') # returning api key to the PATH

    def test_ask(self):
        content_path1 = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        content_path2 = 'sample_contents\\People.xlsx'
        self.ai.add_content(content_path1)
        self.ai.add_content(content_path2)
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question)
        assert isinstance(answear, str) is True

    def test_ask_with_contents(self):
        content_path = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        self.ai.add_content(content_path)
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question, [content_path])
        assert isinstance(answear, str) is True
        self.ai.reset_contents_database()

    def test_history_aware_retriever(self):
        content_path = 'sample_contents\\People.xlsx' 
        self.ai.add_content(content_path)
        docs = self.ai.ha_retriever.invoke({'input': 'Hi!', 'chat_history': []})
        assert isinstance(docs, list)
        assert isinstance(docs[0], Document)

    def test_qa_chain(self):
        content_path1 = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        content_path2 = 'sample_contents\\People.xlsx'
        chat_history = []
        self.ai.add_contents([content_path1, content_path2])
        docs = self.ai.ha_retriever.invoke({'input': 'Hi!', 'chat_history': chat_history})
        answer = self.ai.qa_chain.invoke({'input': 'Hi', 'context': docs, 'chat_history': chat_history})
        assert isinstance(answer, str)

    def test_rag_chain(self):
        content_path1 = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        content_path2 = 'sample_contents\\People.xlsx'
        chat_history = []
        self.ai.add_contents([content_path1, content_path2])
        response = self.ai.rag_chain.invoke({'input': 'Hi!', 'chat_history': chat_history})
        assert set(response.keys()) == set(['answer', 'chat_history', 'context', 'input'])

    def test_create_chat_session(self):
        session_id = 'fapeg chat'
        self.ai.create_chat_session(session_id)
        session = self.ai.get_chat_session(session_id)
        assert not session['sources'] is None
        assert not session['history'] is None

    def test_ask_chat(self):
        content_path = 'sample_contents\\People.xlsx'
        session_id = 'people chat'
        self.ai.add_content(content_path)
        self.ai.create_chat_session(session_id)
        self.ai.add_session_contents(session_id, [content_path])
        answer = self.ai.ask_chat('Be short, what the context is talking about?', session_id)
        assert isinstance(answer, str)

    def test_add_session_contents(self):
        content_path = 'sample_contents\\People.xlsx'
        session_id = 'people chat'
        self.ai.create_chat_session(session_id)
        self.ai.add_session_contents(session_id, [content_path])
        session_contents = self.ai.get_chat_session(session_id)['sources']
        assert content_path in session_contents

    def test_delete_session_content(self):
        content_path = 'sample_contents\\People.xlsx'
        session_id = 'people chat'
        self.ai.create_chat_session(session_id)
        self.ai.add_session_contents(session_id, [content_path])
        self.ai.delete_session_content(session_id, content_path)
        session_contents = self.ai.get_chat_session(session_id)['sources']
        assert not content_path in session_contents