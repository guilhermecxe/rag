from langchain_chroma import Chroma
import os

from .settings import SETTINGS
from .utils import get_embedding_function

class Database:
    def __init__(self):
        self.__initialize_collection()

    def __initialize_collection(self):
        self.db = Chroma(
            collection_name=SETTINGS.get('COLLECTION_NAME'),
            persist_directory=SETTINGS.get('VECTORS_DATABASE_PATH'),
            embedding_function=get_embedding_function()
        )

    def reset_database(self):
        ids = self.db.get(include=[])['ids']
        
        batch_size = 5461  # Set the batch size to the maximum allowed
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i + batch_size]
            self.db.delete(batch)

    def delete_sources_chunks(self, sources:list[str]):
        ids = self.db.get(where={'source': {'$in': sources}})
        self.db.delete(ids)

    def insert_chunks(self, chunks:list):
        self.db.add_documents(chunks)

    def get_unique_sources(self, as_dict=False):
        metadatas = self.db.get()['metadatas']
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

    def search(self, query:str, sources=[]):
        condition = {'source': {'$in': sources}} if sources else {}
        results = self.db.similarity_search(query, k=5, filter=condition)
        return results
