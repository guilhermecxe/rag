import os
from dotenv import load_dotenv
from datetime import date

load_dotenv('.env')

class Settings:
    def __init__(self, **kwargs):
        self._settings = {
            # Parsers
            'CHUNK_SIZE': 1500,
            'CHUNK_OVERLAP': 100,

            # Contents database
            'VECTORS_DATABASE_PATH': 'contents_database',
            'COLLECTION_NAME': 'contents',
            'MAX_CONTEXT_CHUNKS': 40,

            # Chat database
            'CHAT_DATABASE_FOLDER': 'chat_database',
            'CHAT_DATABASE_FILE': 'sessions.pkl',

            # AI Model
            'GPT_MODEL': 'gpt-4o-mini',
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
            'MAX_VISIBLE_CHAT_MESSAGES': 4,
            'SYSTEM_INSTRUCTION': f"""
                Você é um assistente prestativo que não responde se não estiver confiante.
                Hoje é {date.today().strftime('%d/%m/%Y')}.""",
            'PROMPT_TEMPLATE': """
                Responda a pergunta abaixo:
                {question}

                Baseie-se nestas notas para responder a pergunta acima, se necessário:

                {context}""",
            'QA_SYSTEM_PROMP': """
                You are an assistant for question-answering tasks. \
                Use the following pieces of retrieved context to answer the question. \
                If you don't know the answer, just say that you don't know. \
                {context}""",
            'CONTEXTUALIZER_SYSTEM_PROMPT': """
                Given a chat history and the latest user question \
                which might reference context in the chat history, formulate a standalone question \
                which can be understood without the chat history. Do NOT answer the question, \
                just reformulate it if needed and otherwise return it as is."""
        }
        self._settings.update(kwargs)

    def update(self, **kwargs):
        self._settings.update(kwargs)

    def get(self, key):
        return self._settings.get(key)
    
    def set(self, key, value):
        self._settings[key] = value
