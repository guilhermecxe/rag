from rag.database import Database
from rag.settings import Settings

class TestDatabase(object):
    @classmethod
    def setup_class(cls):
        cls.db = Database(Settings())
        print('\nDEBUG: Setup method executed.')

    @classmethod
    def teardown_class(cls):
        cls.db.reset_database()
        print('\nDEBUG: Teardown method executed.')

    def test_get_chunks_count(self):
        chunks_count = self.db.get_chunks_count()
        assert isinstance(chunks_count, int)
        assert chunks_count == 0

    def test_reset_database(self):
        self.db.reset_database()
        assert self.db.get_chunks_count() == 0

    def test_delete_sources_chunks(self):
        pass # for now, only tested indirectly on test_assistant.py

    def test_insert_chunks(self):
        pass # for now, only tested indirectly on test_assistant.py

    def test_get_unique_sources(self):
        unique_sources = self.db.get_unique_sources()
        assert isinstance(unique_sources, list)
        assert len(unique_sources) == 0

    def test_search(self):
        pass # for now, only tested indirectly on test_assistant.py