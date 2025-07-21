import os
from dotenv import load_dotenv
load_dotenv()
#from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI, Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from tempfile import NamedTemporaryFile



class RAGEngine:
    def __init__(self):
            embedding_model = os.getenv("LLM_EMBEDDING_MODEL", "bge-m3")

            self.vectorstore = Chroma(
                        persist_directory="chroma_db",
        embedding_function=OllamaEmbeddings(model=embedding_model))



    def add_document(self, file):
        suffix = os.path.splitext(file.filename)[-1]
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path) if suffix == ".pdf" else TextLoader(tmp_path)
        docs = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(docs)

        self.vectorstore.add_documents(docs)
        self.vectorstore.persist()
        os.remove(tmp_path)

    def query(self, question: str, llm_name: str):
        retriever = self.vectorstore.as_retriever()

        if llm_name == "openai":
            llm = OpenAI()
        elif llm_name == "ollama":
            llm = Ollama(
                model="llama3.2",                     # Change if you use a different LLaMA variant
            base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),  # ✅ Uses env var
                temperature=0.7
            )
        elif llm_name == "gemini":
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
        else:
            return "Unsupported LLM"

        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        return qa.run(question)

