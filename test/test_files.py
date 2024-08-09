import pytest
import os

from rag.files import get_folders, get_files
from rag.settings import SETTINGS

class TestGetFolders(object):
    def test_get_folders(self):
        expected = ['FAPEG', 'Sherlock Holmes']
        actual = get_folders()
        assert actual == expected

class TestGetFiles(object):
    def test_get_files_without_path(self):
        expected = ['Edital nº 08.2024 - Meninas em STEM - 1ª Retificação.pdf', 'Estatuto da FAPEG 2023.pdf']
        actual = get_files('FAPEG')
        assert set(actual) == set(expected)

    def test_get_files_with_path(self):
        expected = [
            (
                'The Adventures of Sherlock Holmes.pdf',
                f"{SETTINGS.get('CONTENTS_PATH')}\\Sherlock Holmes\\The Adventures of Sherlock Holmes.pdf")]
        actual = get_files('Sherlock Holmes', with_path=True)
        assert set(actual) == set(expected)