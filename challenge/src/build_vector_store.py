from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

base_path = "docs"
all_docs = []

for category_folder in Path(base_path).iterdir():
    if category_folder.is_dir():
        category = category_folder.name
        for file in category_folder.glob("*.md"):
            loader = TextLoader(str(file), encoding="utf-8")
            docs = loader.load()
            # Attach metadata (e.g., category)
            for doc in docs:
                doc.metadata["category"] = category

            all_docs.extend(docs)

# Create splitter (tweak sizes as needed)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

# Apply chunking to all documents
chunks = text_splitter.split_documents(all_docs)
embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embedding_model)
vectorstore.save_local("full_index")
