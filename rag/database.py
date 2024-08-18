from langchain.schema.document import Document
import chromadb
from chromadb.config import Settings
import uuid

from .settings import SETTINGS
from .utils import get_embedding_function

class Database:
    def __init__(self):
        self.__initialize_collection()

    def reinitialize(self):
        self.__initialize_collection()

    def __initialize_collection(self):
        client = chromadb.PersistentClient(path=SETTINGS.get('VECTORS_DATABASE_PATH'))
        self.collection = client.get_or_create_collection(
            name=SETTINGS.get('COLLECTION_NAME'),
            embedding_function=get_embedding_function()
        )

    def get_chunks_count(self):
        return len(self.collection.get(include=[])['ids'])

    def reset_database(self):
        ids = self.collection.get(include=[])['ids']
        if ids:
            limit = 5461
            for i in range(0, len(ids), limit):
                self.collection.delete(ids=ids[i:i+limit])

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
        for i in range(0, len(ids), 500):
            self.collection.add(ids=ids[i:i+500], documents=documents[i:i+500], metadatas=metadatas[i:i+500])

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
            distance = query_result['distances'][0][i]
            metadata['similarity'] = 1-distance
            documents.append(Document(page_content=page_content, metadata=metadata))
        return documents
    
    def __filter_documents_by_similarity(self, documents, minimum=0.0):
        return list(filter(lambda d: d.metadata['similarity'] >= minimum, documents))

    def search(self, query:str, sources=[], only_positive_similarities=False):
        condition = {'source': {'$in': sources}} if sources else {}
        results = self.collection.query(query_texts=[query], n_results=SETTINGS['MAX_CONTEXT_CHUNKS'], where=condition)
        documents = self.__query_result_to_documents_list(results)
        if only_positive_similarities:
            documents = self.__filter_documents_by_similarity(documents, minimum=0.0)
        if not documents:
            raise ValueError('No chunks found that meet the similarity criteria.')
        return documents
