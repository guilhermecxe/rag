import pytest
import os

from rag.model import AiModel
from rag.settings import SETTINGS

class TestAiModel(object):
    def setup_method(self):
        self.model = AiModel()

    def test_check_valid_api_key(self):
        assert self.model.check_api_key()

    def test_check_invalid_api_key(self):
        old_api_key = os.environ['OPENAI_API_KEY']
        os.environ['OPENAI_API_KEY'] = 'abc'
        self.model.reset_client()
        assert not self.model.check_api_key()
        os.environ['OPENAI_API_KEY'] = old_api_key

    def test_update_valid_openai_api_key(self):
        assert self.model.update_openai_api_key(os.environ.get('OPENAI_API_KEY'))

    def test_update_invalid_openai_api_key(self):
        assert not self.model.update_openai_api_key('abc')