import pytest
import os
import re

from rag import Assistant
from rag.model import AiModel

class TestAiModel(object):
    @classmethod
    def setup_class(cls):
        cls.model = AiModel()
        print('\nDEBUG: Setup method executed.')

    @classmethod
    def teardown_class(cls):
        pass # not necessary

    def test_check_valid_api_key(self):
        assert self.model.check_api_key()

    def test_check_invalid_api_key(self):
        assert not self.model.check_api_key('abc')

    def test_check_empty_api_key(self):
        assert not self.model.check_api_key(api_key='')

    def test_check_valid_model(self):
        assert self.model.check_model('gpt-4o-mini')

    def test_check_invalid_model(self):
        assert not self.model.check_model('abc')

    def test_check_empty_model(self):
        assert not self.model.check_api_key('')

    def test_update_valid_openai_api_key(self):
        assert self.model.update_openai_api_key(os.environ.get('OPENAI_API_KEY'))

    def test_update_invalid_openai_api_key(self):
        assert not self.model.update_openai_api_key('abc')

    def test_is_suitable_model(self):
        assert self.model.is_suitable_model('gpt-4o-mini')
        assert not self.model.is_suitable_model('whisper-1')

    def test_ask(self):
        answer = self.model.ask('Hi!', context='Just saying hi.')
        assert isinstance(answer, str)