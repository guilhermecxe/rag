from langchain_openai import OpenAIEmbeddings
from chromadb.utils import embedding_functions
import os

from .settings import SETTINGS

def get_embedding_function():
    return OpenAIEmbeddings(openai_api_key=SETTINGS['OPENAI_API_KEY'], model='text-embedding-3-small')
