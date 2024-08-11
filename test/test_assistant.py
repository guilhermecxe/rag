import pytest
import os

from rag.assistant import Assistant
from rag.settings import SETTINGS

class TestAssistant(object):
    def setup_method(self):
        self.ai = Assistant()
        self.ai.reset_database()

    def test_reset_database(self):
        self.ai.reset_database()
        contents = self.ai.get_available_contents(as_dict=False)
        assert len(contents) == 0

    def test_get_new_contents(self):
        contents_path = SETTINGS.get('CONTENTS_PATH')
        expected_contents = [
            'FAPEG\\Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf',
            'FAPEG\\Estatuto da FAPEG 2023.pdf',
            'Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf']
        expected = [os.path.join(contents_path, content) for content in expected_contents]
        actual = self.ai.get_new_contents()
        self.ai.reset_database()
        assert set(actual) == set(expected)

    def test_update_database_and_get_available_contents(self):
        contents_path = SETTINGS.get('CONTENTS_PATH')
        self.ai.update_database()
        expected_contents = [
            'FAPEG\\Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf',
            'FAPEG\\Estatuto da FAPEG 2023.pdf',
            'Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf']
        expected = [os.path.join(contents_path, content) for content in expected_contents]
        actual = self.ai.get_available_contents(as_dict=False)
        self.ai.reset_database()
        assert set(actual) == set(expected)

    def test_add_contents(self):
        content_path = 'contents\\Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf'
        self.ai.add_content(content_path)
        available_contents = self.ai.get_available_contents(as_dict=False)
        self.ai.reset_database()
        assert content_path in available_contents

    def test_delete_contents(self):
        self.ai.update_database()
        content_path = 'contents\\Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf'
        self.ai.delete_contents([content_path])
        assert not content_path in self.ai.get_available_contents(as_dict=False)
        assert 'contents\\FAPEG\\Estatuto da FAPEG 2023.pdf' in self.ai.get_available_contents(as_dict=False)
        self.ai.reset_database()

    def test_ask(self):
        self.ai.update_database()
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question)
        assert isinstance(answear, str) is True
        self.ai.reset_database()

    def test_ask_with_contents(self):
        self.ai.update_database()
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question, {'FAPEG': ['Estatuto da FAPEG 2023.pdf']})
        assert isinstance(answear, str) is True
        self.ai.reset_database()

    def test_ask_with_contents_as_list(self):
        self.ai.update_database()
        question = 'quais as diretorias da fapeg?'
        answear = self.ai.ask(question, ['contents\\FAPEG\\Estatuto da FAPEG 2023.pdf'])
        assert isinstance(answear, str) is True
        self.ai.reset_database()