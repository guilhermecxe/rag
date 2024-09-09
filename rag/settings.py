import os
from dotenv import load_dotenv
from datetime import date

load_dotenv('.env')

SETTINGS = {
    # Files
    'CONTENTS_PATH': 'contents',

    # Database
    'VECTORS_DATABASE_PATH': 'contents_database',
    'CHUNK_SIZE': 1500,
    'CHUNK_OVERLAP': 100,
    'COLLECTION_NAME': 'contents',
    'MAX_CONTEXT_CHUNKS': 40,

    # Chat
    'CHAT_DATABASE_PATH': 'chat_database/sessions.pkl',

    # AI Model
    'GPT_MODEL': 'gpt-4o-mini',
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
    'MAX_CHAT_MESSAGES_VISIBLE': 4,
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
