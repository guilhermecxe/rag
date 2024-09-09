from rag.assistant import Assistant
from rag.settings import SETTINGS

import pytest
import re

class TestUseCases(object):
    @classmethod
    def setup_class(cls):
        SETTINGS['MAX_CONTEXT_CHUNKS'] = 4 # ensuring the value, but maybe not the best way to alter it
        cls.ai = Assistant()
        cls.ai.reset_contents_database()
        cls.ai.reset_chat_database()
        print('\nDEBUG: Setup method executed.')

    @classmethod
    def teardown_class(cls):
        cls.ai.reset_contents_database()
        cls.ai.reset_chat_database()
        print('\nDEBUG: Teardown method executed.')

    def test_chat_history_limit(self):
        content_path1 = 'sample_contents\\Estatuto da FAPEG 2023.pdf'
        content_path2 = 'sample_contents\\People.xlsx'
        session_id = 'people chat'
        self.ai.add_contents([content_path1, content_path2])
        self.ai.create_chat_session(session_id)
        self.ai.add_session_contents(session_id, [content_path1, content_path2])
        self.ai.ask_chat('Be short, what the context is talking about?', session_id)
        self.ai.ask_chat('Write my last question in brazilian portuguese', session_id)
        self.ai.ask_chat('What is the language of the AI last message?', session_id)
        history = self.ai.get_chat_session(session_id)['history']
        model_visible_messages = history.messages
        all_messages = history.all_messages
        assert len(model_visible_messages) == SETTINGS['MAX_CHAT_MESSAGES_VISIBLE'] # expecting 4
        assert len(all_messages) ==  6

    def test_no_chat_content(self):
        session_id = 'chat'
        self.ai.delete_session(session_id) # ensuring empty session
        self.ai.create_chat_session(session_id)
        with pytest.raises(ValueError, match=re.escape((
            '''You must add a content to the chat session to ask something. '''
            '''Try ai.add_session_contents(session_id, [content]).'''))):
            self.ai.ask_chat('Be short, what the context is talking about?', session_id)
