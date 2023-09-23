import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter

# from langchain.document_loaders.unstructured import UnstructuredBaseLoader

# class UnstructuredHtmlStringLoader(UnstructuredBaseLoader):
#     '''
#     Uses unstructured to load a string
#     Source of the string, for metadata purposes, can be passed in by the caller
#     '''

#     def __init__(
#         self, content: str, source: str = None, mode: str = "single",
#         **unstructured_kwargs: Any
#     ):
#         self.content = content
#         self.source = source
#         super().__init__(mode=mode, **unstructured_kwargs)

#     def _get_elements(self) -> List:
#         from unstructured.partition.html import partition_html

#         return partition_html(text=self.content, **self.unstructured_kwargs)

#     def _get_metadata(self) -> dict:
#         return {"source": self.source} if self.source else {}



def get_docs_response(txt):
    # Split text
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(txt)
    # Create multiple documents
    docs = [Document(page_content=t) for t in texts]
    # Text summarization
    return docs

os.environ["OPENAI_API_KEY"] = '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'

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = get_docs_response("My dog's name is Sunny.")

embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query,"chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None