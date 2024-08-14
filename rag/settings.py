import os
from dotenv import load_dotenv
from datetime import date

load_dotenv('.env')

SETTINGS = {
    # Files
    'CONTENTS_PATH': 'contents',

    # Database
    'VECTORS_DATABASE_PATH': 'database',
    'CHUNK_SIZE': 1500,
    'CHUNK_OVERLAP': 100,
    'COLLECTION_NAME': 'contents',
    'MAX_CONTEXT_CHUNKS': 40,

    # AI Model
    'GPT_MODEL': 'gpt-4o-mini',
    'OPENAI_API_KEY': None, # Filled when Assistant is created
    'SYSTEM_INSTRUCTION': f"""
        Você é um assistente prestativo que não responde se não estiver confiante.
        Hoje é {date.today().strftime('%d/%m/%Y')}.""",
    'PROMPT_TEMPLATE': """
        Responda a pergunta abaixo:
        {question}

        Baseie-se nestas notas para responder a pergunta acima, se necessário:

        {context}""",
}
