import pytest
import os

from rag.database import Database
# from rag.settings import SETTINGS

class TestDatabase(object):
    def setup_method(self):
        self.db = Database()

    def test_get_chunks_count(self):
        assert isinstance(self.db.get_chunks_count(), int)

    def test_reset_database(self):
        self.db.reset_database()
        assert self.db.get_chunks_count() == 0

    def test_delete_sources_chunks(self):
        pass

    def test_insert_chunks(self):
        pass

    def test_get_unique_sources(self):
        unique_sources = self.db.get_unique_sources()
        assert isinstance(unique_sources, list)

    def test_search(self):
        pass