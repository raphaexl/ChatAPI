from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain,RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from langchain.document_loaders import YoutubeLoader
# from langchain.chains.summarize import load_summarize_chain

#loader = TextLoader("fatherofnation.txt")
loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=QsYGlZkevEg", add_video_info=True)
documents = loader.load()

template = """Answer the question in your own words from the 
context given to you.
If questions are asked where there is no relevant context available, please answer from 
what you know.

Context: {context}

Human: {question}
Assistant:"""

prompt = PromptTemplate(
input_variables=["context",  "question"], template=template)

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(documents)

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(documents, embedding_function)

llm = "gpt-3.5-turbo"

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

memory.save_context({"input": "Who is the founder of India?"},
                {"output": "Gandhi"})

qa = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever(), memory=memory,chain_type_kwargs={'prompt': prompt}
)

# question = "Who is the father of India nation?"
# result = qa({"query": question})
# print(result)

question1= "What did I ask about India?"
result1 = qa({"query": question1})
print(result1)

question1= "Tell me about google in short ?"
result1 = qa({"query": question1})
print(result1)