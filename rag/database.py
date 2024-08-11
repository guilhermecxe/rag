from langchain.schema.document import Document
import chromadb
from chromadb.config import Settings
import uuid

from .settings import SETTINGS
from .utils import get_embedding_function

class Database:
    def __init__(self):
        self.__initialize_collection()

    def __initialize_collection(self):
        client = chromadb.Client(Settings(persist_directory=SETTINGS.get('VECTORS_DATABASE_PATH')))
        self.collection = client.get_or_create_collection(
            name=SETTINGS.get('COLLECTION_NAME'),
            embedding_function=get_embedding_function()
        )

    def get_chunks_count(self):
        return len(self.collection.get(include=[])['ids'])

    def reset_database(self):
        ids = self.collection.get(include=[])['ids']
        if ids:
            self.collection.delete(ids=ids)

    def delete_sources_chunks(self, sources:list[str]):
        ids = self.collection.get(include=[], where={'source': {'$in': sources}})['ids']
        if ids:
            self.collection.delete(ids=ids)

    def insert_chunks(self, chunks:list):
        ids, documents, metadatas = [], [], []
        for chunk in chunks:
            ids.append(str(uuid.uuid4()))
            documents.append(chunk.page_content)
            metadatas.append(chunk.metadata)
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def get_unique_sources(self, as_dict=False):
        metadatas = self.collection.get(include=['metadatas'])['metadatas']
        source_paths = list(set([data['source'] for data in metadatas]))
        if as_dict:
            folders = [path.split('\\')[-2] for path in source_paths]
            sources = {k: [] for k in folders}
            for path in source_paths:
                folder = path.split('\\')[-2]
                file = path.split('\\')[-1]
                sources[folder].append(file)
            return sources
        else:
            return source_paths
        
    def __query_result_to_documents_list(self, query_result):
        documents = []
        for i in range(len(query_result['ids'][0])):
            page_content = query_result['documents'][0][i]
            metadata = query_result['metadatas'][0][i]
            documents.append(Document(page_content=page_content, metadata=metadata))
        return documents

    def search(self, query:str, sources=[]):
        condition = {'source': {'$in': sources}} if sources else {}
        results = self.collection.query(query_texts=[query], n_results=5, where=condition)
        documents = self.__query_result_to_documents_list(results)
        return documents
