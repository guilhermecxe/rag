from .database import Database
from .chat_database import ChatDatabase
from .parsers import PdfParser, XlsxParser
from .model import AiModel
from .settings import SETTINGS

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import os

class Assistant:
    def __init__(self, openai_api_key=None, gpt_model=None):
        SETTINGS['OPENAI_API_KEY'] = openai_api_key if openai_api_key else os.environ.get('OPENAI_API_KEY')
        
        if gpt_model:
            SETTINGS['GPT_MODEL'] = gpt_model # trusting gpt_model is suitable

        self._contents_db = Database()
        self._chat_db = ChatDatabase()
        self._model = AiModel()

        self.current_chat_contents = []
        # self.last_question = ''
        # self.last_context = ''

        self.ha_retriever = self.__create_history_aware_retriever()
        self.qa_chain = self.__create_qa_chain()
        self.rag_chain = self.__create_rag_chain()
        self._chat = self.__create_chat()

    def get_available_contents(self):
        """
        Returns a list of the path of the contents available in the database.
        """
        return self._contents_db.get_unique_sources()
    
    def get_contents_max_size(self):
        return {
            'pdf': PdfParser.MAX_SIZE,
            'xlsx': XlsxParser.MAX_SIZE,
        }

    def add_content(self, path):
        """
        Add the content with the specified path to the database.
        Not add it if the path is already present in the database.
        """
        if path in self.get_available_contents():
            return
        
        if path.endswith('.pdf'):
            documents = PdfParser.load_pdf(path)
            chunks = PdfParser.split_documents(documents)
        elif path.endswith('.xlsx'):
            documents = XlsxParser.load_xlsx(path)
            chunks = XlsxParser.split_documents(documents)
        self._contents_db.insert_chunks(chunks)

    def add_contents(self, paths:list[str]):
        """
        Add the contents with the specified paths to the database.
        Not add it if the path is already present in the database.
        """
        for path in paths:
            self.add_content(path)

    def delete_contents(self, contents_path):
        """
        Delete the content with the specified path from the database.
        """
        self._contents_db.delete_sources_chunks(contents_path)

    def reset_contents_database(self):
        '''
        Delete all the contents from the database.
        '''
        self._contents_db.reset_database()

    def reset_chat_database(self):
        '''
        Delete all the chat history.
        '''
        self._chat_db.reset_database()

    def check_api_key(self, api_key=None):
        return self._model.check_api_key(api_key)
    
    def check_model(self, model=None):
        return self._model.check_model(model)
    
    def is_suitable_model(self, model=None):
        return self._model.is_suitable_model(model)

    def update_settings(self, **kwargs):
        openai_api_key = kwargs.get('openai_api_key', None)
        gpt_model = kwargs.get('gpt_model', None)

        if openai_api_key:
            if self.check_api_key(openai_api_key):
                self._model.update_openai_api_key(openai_api_key)
                SETTINGS['OPENAI_API_KEY'] = openai_api_key
                self._contents_db.reinitialize() # to the embedding function get the new openai api key
            else:
                raise ValueError("Invalid OpenAI API key")
        
        if gpt_model:
            if self.check_model(gpt_model):
                if self._model.is_suitable_model(gpt_model):
                    SETTINGS['GPT_MODEL'] = gpt_model
                else:
                    raise ValueError(
                        f'''It appears that the model being used ({SETTINGS['GPT_MODEL']}) '''
                         '''is not suitable for this purpose.''')
            else:
                raise ValueError('Invalid GPT Model')
        
        return True
    
    def __create_history_aware_retriever(self, contents:list[str]=[]):
        """
        Returns a retriever that reelaborates the user query based on the previous
        context so the model can answer it without accessing all the chat history.
        """
        contextualizer_prompt = ChatPromptTemplate.from_messages([
            ("system", SETTINGS['CONTEXTUALIZER_SYSTEM_PROMPT']),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")])

        ha_retriever = create_history_aware_retriever(
            self._model.get_client_model(), self._contents_db.get_retriever(contents), contextualizer_prompt)
        return ha_retriever

    def __create_qa_chain(self):
        """
        Returns a model that receives a list of documents and a question and answers it
        with the documents as context.
        """        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", SETTINGS['QA_SYSTEM_PROMP']),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")])

        qa_chain = create_stuff_documents_chain(self._model.get_client_model(), qa_prompt)
        return qa_chain
    
    def ask(self, question, contents={}):
        relevant_chunks = self._contents_db.search(question, sources=contents)
        answer = self.qa_chain.invoke({'input': question, 'context': relevant_chunks, 'chat_history': []})
        self.last_question = question
        self.last_context = relevant_chunks
        return answer
    
    def __create_rag_chain(self, contents:list[str]=[]):
        """
        Creates the chat chain.
        """
        self.ha_retriever = self.__create_history_aware_retriever(contents)
        self.qa_chain = self.__create_qa_chain()
        rag_chain = create_retrieval_chain(self.ha_retriever, self.qa_chain)
        return rag_chain
    
    def __create_chat(self):
        return self.update_chat(contents=[])

    def update_chat(self, contents:list[str]):
        """
        Recreates the chat instance.
        Can be used to apply changes on attributes used to create it.
        """
        rag_chain = self.__create_rag_chain(contents)
        self.current_chat_contents = contents

        self._chat = RunnableWithMessageHistory(
            runnable=rag_chain,
            get_session_history=self._chat_db.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        return self._chat

    def create_chat_session(self, session_id:str):
        self._chat_db.create_session(session_id)

    def get_chat_session(self, session_id:str):
        return self._chat_db.get_session(session_id)

    def ask_chat(self, question, session_id=None):
        session_contents = self._chat_db.get_session_sources(session_id)
        if not session_contents:
            raise ValueError((
                '''You must add a content to the chat session to ask something. '''
                '''Try ai.add_session_contents(session_id, [content]).'''))
        if set(self.current_chat_contents) != set(session_contents):
            self.update_chat(session_contents)

        response = self._chat.invoke({'input': question}, config={"configurable": {"session_id": session_id}})
        self._chat_db.save_sessions()
        return response['answer']
    
    def add_session_contents(self, session_id:str, contents:list[str]):
        self._chat_db.add_session_sources(session_id, contents)
        self._chat_db.save_sessions()

    def delete_session_content(self, session_id:str, content:str):
        self._chat_db.delete_session_source(session_id, content)

    def delete_session(self, session_id:str):
        self._chat_db.delete_session(session_id)
        self._chat_db.save_sessions()

    def delete_all_sessions(self):
        self._chat_db.delete_sessions()
        self._chat_db.save_sessions()
