from .database import Database
from .files import get_all_files, tree_to_list
from .parsers import PdfParser
from .model import AiModel

class Assistant:
    def __init__(self):
        self.db = Database()

    def __parse_context(self, chunks):
        chunks_text = []
        for chunk in chunks:
            chunks_text.append(
                f"""{chunk.page_content}\n\nSource: {chunk.metadata['source']}""")
        return '\n\n---\n'.join(chunks_text)

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
        sources = tree_to_list(contents)
        relevant_chunks = self.db.search(question, sources=sources)
        context = self.__parse_context(relevant_chunks)

        model = AiModel()
        
        answear = model.ask(question, context)

        return answear
