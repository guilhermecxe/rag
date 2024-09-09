from langchain.schema.document import Document
from langchain_chroma import Chroma

from .settings import SETTINGS
from .utils import get_embedding_function

class Database:
    def __init__(self):
        self._client = self.__initialize_client()

    def reinitialize(self):
        """
        Reinitializes the Chroma instance used to manage the chroma database client.
        Can be used to apply changes on attributes used to initialize it
        on __initialize_client method.
        """
        self._client = self.__initialize_client()

    def __initialize_client(self):
        """
        Defines the Chroma instance to manage the chroma database client.
        """
        return Chroma(
            persist_directory=SETTINGS.get('VECTORS_DATABASE_PATH'),
            embedding_function=get_embedding_function(),
            # embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="distiluse-base-multilingual-cased-v1")
        )

    def get_retriever(self, sources:list[str]):
        filter = {'source': {'$in': sources}} if sources else {}
        return self._client.as_retriever(
            search_kwargs={'filter': filter, 'k': SETTINGS['MAX_CONTEXT_CHUNKS']})
    
    def get_chunks_count(self):
        """
        Returns the count of chunks present in the database.
        """
        return len(self._client.get(include=[])['ids'])

    def reset_database(self):
        '''
        Delete all chunks from the database collection, keeping the collection itself.
        '''
        ids = self._client.get(include=[])['ids']
        if ids:
            batch_size = 5461
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i+batch_size]
                self._client.delete(ids=batch)

    def delete_sources_chunks(self, sources:list[str]):
        '''
        Delete all chunks from the specified sources.
        '''
        ids = self._client.get(where={'source': {'$in': sources}}, include=[])['ids']
        if ids:
            self._client.delete(ids=ids)

    def insert_chunks(self, chunks:list[Document]):
        '''
        Insert chunks into the collection.
        '''
        self._client.add_documents(chunks)

    def get_unique_sources(self):
        '''
        Return the unique sources of the chunks in the collection.
        '''
        metadatas = self._client.get(include=['metadatas'])['metadatas']
        source_paths = list(set([data['source'] for data in metadatas]))
        return source_paths

    def search(self, query:str, sources=[]):
        """
        Returns the `MAX_CONTEXT_CHUNKS` chunks most similar to the query. 
        """
        condition = {'source': {'$in': sources}} if sources else {}
        results = self._client.similarity_search(query=query, k=SETTINGS['MAX_CONTEXT_CHUNKS'], filter=condition)
        return results
    