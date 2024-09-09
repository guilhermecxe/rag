from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage
import pickle
import os

from rag.settings import SETTINGS

class ControlledChatMessageHistory(ChatMessageHistory):
    all_messages = []

    def add_message(self, message: BaseMessage) -> None:
        super().add_message(message)
        self.all_messages.append(message)
        if len(self.messages) > SETTINGS['MAX_CHAT_MESSAGES_VISIBLE']:
            self.messages.pop(0)

class ChatDatabase:
    def __init__(self):
        self.sessions = self.__read_sessions()

    def __read_sessions(self):
        if not os.path.exists(SETTINGS['CHAT_DATABASE_PATH']):
            self.sessions = {'sources': {}, 'history': {}}
            self.save_sessions()

        with open(SETTINGS['CHAT_DATABASE_PATH'], 'rb') as f:
            sessions = pickle.load(f)
        return sessions
    
    def save_sessions(self):
        with open(SETTINGS['CHAT_DATABASE_PATH'], 'wb') as f:
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
        del self.sessions['sources'][session_id]
        del self.sessions['history'][session_id]

    def delete_sessions(self):
        self.sessions = {'history': {}, 'sources': {}}
        