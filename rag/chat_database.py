from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage
import pickle
import os

from rag.settings import Settings

class ControlledChatMessageHistory(ChatMessageHistory):
    all_messages = []

    def add_message(self, message: BaseMessage) -> None:
        global max_visible_chat_messages
        super().add_message(message)
        self.all_messages.append(message)
        if len(self.messages) > max_visible_chat_messages:
            self.messages.pop(0)

class ChatDatabase:
    def __init__(self, settings:Settings):
        self._settings = settings
        self._db_path = os.path.join(self._settings.get('CHAT_DATABASE_FOLDER'), self._settings.get('CHAT_DATABASE_FILE'))
        self.sessions = self.__read_sessions()

        global max_visible_chat_messages
        max_visible_chat_messages = self._settings.get('MAX_VISIBLE_CHAT_MESSAGES')

    def __read_sessions(self):
        if not os.path.exists(self._settings.get('CHAT_DATABASE_FOLDER')):
            os.mkdir(self._settings.get('CHAT_DATABASE_FOLDER'))
        if not os.path.exists(self._db_path):
            self.sessions = {'sources': {}, 'history': {}}
            self.save_sessions()

        with open(self._db_path, 'rb') as f:
            sessions = pickle.load(f)
        return sessions
    
    def save_sessions(self):
        with open(self._db_path, 'wb') as f:
            pickle.dump(self.sessions, f)

    def reset_database(self):
        self.sessions = {'sources': {}, 'history': {}}
        self.save_sessions()

    def create_session(self, session_id:str):
        if session_id in self.sessions['history']:
            return
        self.sessions['sources'][session_id] = []
        self.sessions['history'][session_id] = ControlledChatMessageHistory()

    def __get_session_something(self, session_id:str, thing:str):
        return self.sessions[thing].get(session_id, None)

    def get_session_history(self, session_id:str):
        return self.__get_session_something(session_id, 'history')
    
    def get_session_all_history(self, session_id:str):
        return self.__get_session_something(session_id, 'history').all_messages

    def get_session_sources(self, session_id:str):
        return self.__get_session_something(session_id, 'sources')
    
    def get_session(self, session_id:str):
        return {
            'sources': self.get_session_sources(session_id),
            'history': self.get_session_history(session_id)}

    def add_session_sources(self, session_id:str, sources:list[str]):
        session_sources = self.sessions['sources'][session_id]
        self.sessions['sources'][session_id] = list(set(session_sources + sources))

    def delete_session_source(self, session_id:str, source:str):
        self.sessions['sources'][session_id].remove(source)

    def delete_session(self, session_id:str):
        if session_id in self.sessions['sources']:
            del self.sessions['sources'][session_id]
            del self.sessions['history'][session_id]

    def delete_sessions(self):
        self.sessions = {'history': {}, 'sources': {}}
