import pytest
import os

from rag.assistant import Assistant
from rag.settings import SETTINGS

class TestAssistant(object):
    def setup_method(self):
        self.ass = Assistant()
        self.ass.reset_database()

    def test_reset_database(self):
        self.ass.reset_database()
        contents = self.ass.get_available_contents(as_dict=False)
        assert len(contents) == 0

    def test_get_new_contents(self):
        contents_path = SETTINGS.get('CONTENTS_PATH')
        expected_contents = [
            'FAPEG\\Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf',
            'FAPEG\\Estatuto da FAPEG 2023.pdf',
            'Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf']
        expected = [os.path.join(contents_path, content) for content in expected_contents]
        actual = self.ass.get_new_contents()
        assert set(actual) == set(expected)

    def test_update_database_and_get_available_contents(self):
        contents_path = SETTINGS.get('CONTENTS_PATH')
        self.ass.update_database()
        expected_contents = [
            'FAPEG\\Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf',
            'FAPEG\\Estatuto da FAPEG 2023.pdf',
            'Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf']
        expected = [os.path.join(contents_path, content) for content in expected_contents]
        actual = self.ass.get_available_contents(as_dict=False)
        self.ass.reset_database()
        assert set(actual) == set(expected)

    def test_ask(self):
        question = 'quais as diretorias da fapeg?'
        answear = self.ass.ask(question)
        assert isinstance(answear, str) is True

    def test_ask_with_contents(self):
        question = 'quais as diretorias da fapeg?'
        answear = self.ass.ask(question, {'FAPEG': ['Estatuto da FAPEG 2023.pdf']})
        assert isinstance(answear, str) is True
        