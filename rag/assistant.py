from .database import Database
from .files import get_all_files
from .parsers import PdfParser, XlsxParser
from .model import AiModel
from .settings import SETTINGS

import os

class Assistant:
    def __init__(self):
        self.db = Database()
        self.model = AiModel()
        self.last_context = ''

    def __parse_context(self, chunks):
        chunks_text = []
        for chunk in chunks:
            chunks_text.append(
                f"{chunk.page_content}\n\nSource: {chunk.metadata['source']}")
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
        pdf = list(filter(lambda file: file.endswith('.pdf'), new_files))
        xlsx = list(filter(lambda file: file.endswith('.xlsx'), new_files))
        if pdf:
            documents = PdfParser.load_pdfs(pdf)
            chunks = PdfParser.split_documents(documents)
            self.db.insert_chunks(chunks)
        if xlsx:
            print('iniciou xlsx')
            documents = XlsxParser.load_xlsxs(xlsx)
            chunks = XlsxParser.split_documents(documents)
            self.db.insert_chunks(chunks)
            print('finalizou xlsx')

    def add_content(self, path):
        if path.endswith('.pdf'):
            documents = PdfParser.load_pdf(path)
            chunks = PdfParser.split_documents(documents)
        elif path.endswith('.xlsx'):
            documents = XlsxParser.load_xlsx(path)
            chunks = XlsxParser.split_documents(documents)
        self.db.insert_chunks(chunks)

    def delete_contents(self, contents_path):
        self.db.delete_sources_chunks(contents_path)

    def reset_database(self):
        self.db.reset_database()

    def update_settings(self, **kwargs):
        openai_api_key = kwargs.get('openai_api_key', None)
        if openai_api_key and not self.model.update_openai_api_key(openai_api_key):
            raise ValueError("Invalid OpenAI API key")
        return True

    def ask(self, question, contents={}, only_positive_similarities=False):
        sources = self.__parse_contents(contents) if isinstance(contents, dict) else contents
        relevant_chunks = self.db.search(question, sources, only_positive_similarities)
        context = self.__parse_context(relevant_chunks)
        
        answear = self.model.ask(question, context)

        self.last_context = context

        return answear
