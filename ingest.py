import os
import pickle
import faiss
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

load_dotenv()

DATA_DIR = "data"
STORE_DIR = "rag_store"
os.makedirs(STORE_DIR, exist_ok=True)

def load_documents():
    """Load documents from the data directory."""
    docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
                content = f.read()
                docs.append(Document(page_content=content))
    return docs

def main():
    docs = load_documents()
    if not docs:
        print("No documents found in data/.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"
    )

    vectors = [embeddings.embed_query(doc.page_content) for doc in split_docs]
    dim = len(vectors[0])

    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    faiss.write_index(index, os.path.join(STORE_DIR, "index.faiss"))
    with open(os.path.join(STORE_DIR, "store.pkl"), "wb") as f:
        pickle.dump(split_docs, f)

    print("Ingestion completed. Index and store saved.")

if __name__ == "__main__":
    main()
