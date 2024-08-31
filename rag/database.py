from langchain.schema.document import Document
from langchain_chroma import Chroma

from .settings import SETTINGS
from .utils import get_embedding_function

class Database:
    def __init__(self):
        self.__initialize_collection()

    def reinitialize(self):
        self.__initialize_collection()

    def __initialize_collection(self):
        """
        Defines the Chroma instance to manage the chroma database client.
        """
        self.db = Chroma(
            persist_directory=SETTINGS.get('VECTORS_DATABASE_PATH'),
            embedding_function=get_embedding_function(),
            # embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="distiluse-base-multilingual-cased-v1")
        )
    
    def get_chunks_count(self):
        """
        Returns the count of chunks present in the database.
        """
        return len(self.db.get(include=[])['ids'])

    def reset_database(self):
        '''
        Delete all chunks from the database, keeping the collection itself.
        '''
        ids = self.db.get(include=[])['ids']
        if ids:
            batch_size = 5461
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i+batch_size]
                self.db.delete(ids=batch)

    def delete_sources_chunks(self, sources:list[str]):
        '''
        Delete all chunks from the specified sources.
        '''
        ids = self.db.get(where={'source': {'$in': sources}}, include=[])['ids']
        if ids:
            self.db.delete(ids=ids)

    def insert_chunks(self, chunks:list[Document]):
        '''
        Insert chunks into the collection.
        '''
        self.db.add_documents(chunks)

    def get_unique_sources(self):
        '''
        Return the unique sources of the chunks in the collection.
        '''
        metadatas = self.db.get(include=['metadatas'])['metadatas']
        source_paths = list(set([data['source'] for data in metadatas]))
        return source_paths

    def search(self, query:str, sources=[]):
        """
        Return N chunks most similar to the query. 
        """
        condition = {'source': {'$in': sources}} if sources else {}
        results = self.db.similarity_search(query=query, k=SETTINGS['MAX_CONTEXT_CHUNKS'], filter=condition)
        return results
    