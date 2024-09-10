from langchain_openai import OpenAIEmbeddings
from chromadb.utils import embedding_functions
import os

def get_embedding_function(api_key):
    return OpenAIEmbeddings(openai_api_key=api_key, model='text-embedding-3-small')
