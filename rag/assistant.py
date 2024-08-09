from .database import Database
from .files import get_all_files
from .parsers import PdfParser
from .model import AiModel
from .settings import SETTINGS

import os

class Assistant:
    def __init__(self):
        self.db = Database()

    def __parse_context(self, chunks):
        chunks_text = []
        for chunk in chunks:
            chunks_text.append(
                f"""{chunk.page_content}\n\nSource: {chunk.metadata['source']}""")
        return '\n\n---\n'.join(chunks_text)
    
    def __parse_contents(self, contents):
        file_paths = []
        for folder, files in contents.items():
            for file in files:
                path = os.path.join(SETTINGS.get('CONTENTS_PATH'), folder, file)
                file_paths.append(path)
        return file_paths

    def get_new_contents(self):
        database_sources = self.db.get_unique_sources(as_dict=False)
        available_contents = get_all_files()
        return list(set(available_contents) - set(database_sources))

    def get_available_contents(self, as_dict=True):
        return self.db.get_unique_sources(as_dict=as_dict)

    def update_database(self):
        new_files = self.get_new_contents()
        if new_files:
            documents = PdfParser.load_pdfs(new_files)
            chunks = PdfParser.split_documents(documents)
            self.db.insert_chunks(chunks)

    def reset_database(self):
        self.db.reset_database()

    def ask(self, question, contents={}):
        sources = self.__parse_contents(contents)
        relevant_chunks = self.db.search(question, sources=sources)
        context = self.__parse_context(relevant_chunks)

        model = AiModel()
        
        answear = model.ask(question, context)

        return answear
