from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema.document import Document

from .settings import Settings

import pandas as pd
import os

class ParserInterface:
    MAX_SIZE = None

    def __init__(self, settings:Settings):
        self._settings = settings

    def split_documents(self, documents:list[Document], separators:list[str]=['\n\n', '\n', '.', ' ', '']):
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=self._settings.get('CHUNK_SIZE'),
            chunk_overlap=self._settings.get('CHUNK_OVERLAP'),
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        return chunks

class PdfParser(ParserInterface):
    MAX_SIZE = 20000 # KB

    def load_pdf(self, file_path:str) -> list:
        file_size = os.path.getsize(file_path) / 1000
        if file_size > PdfParser.MAX_SIZE:
            raise OSError(
                f'''File size {int(file_size)} KB exceeds the maximum allowed '''
                f'''size of {PdfParser.MAX_SIZE} KB. File path: {file_path}.''')

        return PyMuPDFLoader(file_path).load_and_split()
    
    def load_pdfs(self, paths:list[str]):
        documents = []
        for file in paths:
            documents += PdfParser.load_pdf(file)
        return documents

class XlsxParser(ParserInterface):
    MAX_SIZE = 2000 # KB

    def load_xlsx(self, file_path:str) -> list[Document]:
        file_size = os.path.getsize(file_path) / 1000
        if file_size > XlsxParser.MAX_SIZE:
            raise OSError(
                f'''File size {int(file_size)} KB exceeds the maximum allowed '''
                f'''size of {XlsxParser.MAX_SIZE} KB. File path: {file_path}.''')

        df = pd.read_excel(file_path)
        columns = df.columns
        text = ''
        for i, row in df.iterrows():
            for col in columns:
                text += (
                    f"""{row[col]}\n"""
                )
            text += "\n"
        document = Document(page_content=text, metadata={'source': file_path})
        return [document]
    
    def load_xlsxs(self, paths:list[str]):
        documents = []
        for file in paths:
            documents += XlsxParser.load_xlsx(file)
        return documents
