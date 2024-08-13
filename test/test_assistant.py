import pytest
import os

from rag.assistant import Assistant
from rag.settings import SETTINGS

class TestAssistant(object):
    def setup_method(self):
        self.ai = Assistant()
        self.ai.reset_database()
        self.__class__.instance = self 

    @classmethod
    def teardown_class(cls):
        cls.instance.ai.reset_database()

    def test_reset_database(self):
        contents = self.ai.get_available_contents(as_dict=False)
        assert len(contents) == 0

    def test_get_new_contents(self):
        contents_path = SETTINGS.get('CONTENTS_PATH')
        expected_contents = [
            'FAPEG\\Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf',
            'FAPEG\\Estatuto da FAPEG 2023.pdf',
            'Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf',
            'Xlsx\\file_example_XLS_100.xlsx']
        expected = [os.path.join(contents_path, content) for content in expected_contents]
        actual = self.ai.get_new_contents()
        assert set(actual) == set(expected)

    def test_update_database_and_get_available_contents(self):
        contents_path = SETTINGS.get('CONTENTS_PATH')
        self.ai.update_database()
        expected_contents = [
            'FAPEG\\Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf',
            'FAPEG\\Estatuto da FAPEG 2023.pdf',
            'Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf',
            'Xlsx\\file_example_XLS_100.xlsx']
        expected = [os.path.join(contents_path, content) for content in expected_contents]
        actual = self.ai.get_available_contents(as_dict=False)
        assert set(actual) == set(expected)

    def test_add_content(self):
        content_path = 'contents\\Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf'
        self.ai.delete_contents([content_path])
        self.ai.add_content(content_path)
        available_contents = self.ai.get_available_contents(as_dict=False)
        assert content_path in available_contents

    def test_add_content_xlsx(self):
        content_path = 'contents\\Xlsx\\file_example_XLS_100.xlsx'
        self.ai.delete_contents([content_path])
        self.ai.add_content(content_path)
        available_contents = self.ai.get_available_contents(as_dict=False)
        assert content_path in available_contents
        self.ai.reset_database()

    def test_delete_contents(self):
        content_path1 = 'contents\\Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf'
        content_path2 = 'contents\\FAPEG\\Estatuto da FAPEG 2023.pdf'
        self.ai.add_content(content_path1)
        self.ai.add_content(content_path2)
        self.ai.delete_contents([content_path1])
        available_contents = self.ai.get_available_contents(as_dict=False)
        assert not content_path1 in available_contents
        assert content_path2 in available_contents
        self.ai.reset_database()

    def test_check_valid_api_key(self):
        assert self.ai.check_api_key()

    def test_check_invalid_api_key(self):
        assert not self.ai.check_api_key('abc')

    def test_update_valid_settings(self):
        assert self.ai.update_settings(openai_api_key=os.environ['OPENAI_API_KEY'])

    def test_update_invalid_settings(self):
        with pytest.raises(ValueError, match='Invalid OpenAI API key'):
            self.ai.update_settings(openai_api_key='abc')

    def test_ask(self):
        content_path = 'contents\\FAPEG\\Estatuto da FAPEG 2023.pdf'
        self.ai.add_content(content_path)
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question)
        assert isinstance(answear, str) is True
        self.ai.reset_database()

    def test_ask_with_contents(self):
        content_path = 'contents\\FAPEG\\Estatuto da FAPEG 2023.pdf'
        self.ai.add_content(content_path)
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question, {'FAPEG': ['Estatuto da FAPEG 2023.pdf']})
        assert isinstance(answear, str) is True
        self.ai.reset_database()

    def test_ask_with_contents_as_list(self):
        content_path = 'contents\\FAPEG\\Estatuto da FAPEG 2023.pdf'
        self.ai.add_content(content_path)
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question, ['contents\\FAPEG\\Estatuto da FAPEG 2023.pdf'])
        assert isinstance(answear, str) is True

    def test_ask_with_only_positive_similarities(self):
        content_path = 'contents\\Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf'
        self.ai.add_content(content_path)
        question = 'quais as diretorias da fapeg?'
        with pytest.raises(ValueError, match='No chunks found that meet the similarity criteria.'):
            self.ai.ask(question, [content_path], only_positive_similarities=True)