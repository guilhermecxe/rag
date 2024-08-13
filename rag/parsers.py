from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema.document import Document

from .settings import SETTINGS
from .files import get_all_files

import pandas as pd
import os

class PdfParser:
    MAX_SIZE = 20000 # KB

    def load_pdf(file_path:str) -> list:
        file_size = os.path.getsize(file_path) / 1000
        if file_size > PdfParser.MAX_SIZE:
            raise OSError(
                f'''File size {int(file_size)} KB exceeds the maximum allowed '''
                f'''size of {PdfParser.MAX_SIZE} KB. File path: {file_path}.''')

        return PyMuPDFLoader(file_path).load_and_split()
    
    def load_pdfs(paths:list[str]):
        documents = []
        for file in paths:
            documents += PdfParser.load_pdf(file)
        return documents

    def load_all_pdfs() -> list:
        files = get_all_files()
        documents = []
        for file in files:
            documents += PdfParser.load_pdf(file)
        return documents

    def split_documents(documents:list) -> list:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ' ', ''],
            chunk_size=SETTINGS.get('CHUNK_SIZE'),
            chunk_overlap=SETTINGS.get('CHUNK_OVERLAP'),
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        return chunks

class XlsxParser:
    MAX_SIZE = 2000 # KB

    def load_xlsx(file_path:str) -> list[Document]:
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
    
    def load_xlsxs(paths:list[str]):
        documents = []
        for file in paths:
            documents += XlsxParser.load_xlsx(file)
        return documents
    
    def split_documents(document:str):
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '---', '\n'],
            chunk_size=SETTINGS.get('CHUNK_SIZE'),
            chunk_overlap=0,
            length_function=len,
        )
        chunks = text_splitter.split_documents(document)
        return chunks