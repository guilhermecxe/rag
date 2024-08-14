import pytest
import os
import re

from rag import Assistant
from rag.model import AiModel

class TestAiModel(object):
    def setup_method(self):
        self.ai = Assistant()
        self.model = AiModel()

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

    def test_ask_with_wrong_model(self):
        wrong_model = 'whisper-1'
        self.ai.update_settings(gpt_model=wrong_model)
        expected_error_message = (
            f'''It appears that the model being used ({wrong_model}) '''
             '''is not the suitable for this purpose.''')
        with pytest.raises(ValueError, match=re.escape(expected_error_message)):
            self.model.ask('question', 'context')
