from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader

from .settings import SETTINGS
from .files import get_all_files

class PdfParser:
    def load_pdf(file_path:str) -> list:
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
    