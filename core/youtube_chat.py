from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationChain, ConversationalRetrievalChain

from dotenv import find_dotenv, load_dotenv
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
import textwrap
import sys

load_dotenv(find_dotenv())
embeddings = OpenAIEmbeddings()


def create_db_from_youtube_video_url(video_url):
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    return db

def get_docs_response(txt):
    # Split text
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(txt)
    # Create multiple documents
    docs = [Document(page_content=t) for t in texts]
    # Text summarization
    return docs

def get_response_from_query(docs):
    chat = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.2)

    # Template to use for the system message prompt
    template = """
        You are a helpful assistant that that can answer questions about youtube videos 
        based on the video's transcript: {docs}
        
        Only use the factual information from the transcript to answer the question.
        
        If you feel like you don't have enough information to answer the question, say "I don't know".
        
        """
    #documents = get_docs_response(template)

    #vectorstore = Chroma.from_documents(documents, embeddings)
    # vectordb = Chroma.from_documents(docs, embedding=OpenAIEmbeddings(), persist_directory="./data")
    # vectordb.persist()
    vectordb = db
    #chain = LLMChain(llm=chat, prompt=chat_prompt, memory=ConversationBufferMemory())
    # chain = ConversationChain(llm=chat, prompt=chat_prompt)
    chain =  ConversationalRetrievalChain.from_llm(
    llm=chat,
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
    )

    return chain

    #response = chain.run(question=query, docs=docs_page_content)
    response = chain.predict({"question":query, "chat_history": chat_history, "docs":docs_page_content})
    response = response.replace("\n", "")
    return response, docs


# Example usage:
video_url = "https://www.youtube.com/watch?v=th4j9JxWGko"
chat_history = []

db = create_db_from_youtube_video_url(video_url)

query = "what is this video about?"

chain = get_response_from_query(db)
result = chain({"question": query, "chat_history": chat_history})
print(textwrap.fill(result["answer"], width=50))
chat_history.append((query, result["answer"]))
query = None
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query, "chat_history": chat_history})
  #response, docs = get_response_from_query(db, query, chat_history)
  print(textwrap.fill(result["answer"], width=50))
  #print(result['answer'])
  chat_history.append((query, result["answer"]))
  query = None