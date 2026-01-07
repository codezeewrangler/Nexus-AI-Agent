import os
import faiss
import pickle
from typing import List

from pypdf import PdfReader
from docx import Document as DocxDocument
from sentence_transformers import SentenceTransformer
import numpy as np

VECTOR_STORE_PATH = "data/vectorstore/faiss.index"
DOC_STORE_PATH = "data/vectorstore/docs.pkl"

# Load embedding model (free, local)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def load_documents(doc_folder: str) -> List[str]:
    texts = []

    for filename in os.listdir(doc_folder):
        path = os.path.join(doc_folder, filename)

        if filename.endswith(".pdf"):
            reader = PdfReader(path)
            for page in reader.pages:
                texts.append(page.extract_text())

        elif filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                texts.append(f.read())

        elif filename.endswith(".docx"):
            doc = DocxDocument(path)
            doc_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            if doc_text:
                texts.append(doc_text)

    return [t for t in texts if t]


def build_vector_store():
    docs = load_documents("data/documents")

    embeddings = embedding_model.encode(docs)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, VECTOR_STORE_PATH)

    with open(DOC_STORE_PATH, "wb") as f:
        pickle.dump(docs, f)


def load_vector_store():
    index = faiss.read_index(VECTOR_STORE_PATH)

    with open(DOC_STORE_PATH, "rb") as f:
        docs = pickle.load(f)

    return index, docs


def retrieve_context(query: str, k: int = 3) -> str:
    if not os.path.exists(VECTOR_STORE_PATH):
        return ""

    index, docs = load_vector_store()

    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k)

    retrieved = [docs[i] for i in indices[0] if i < len(docs)]
    return "\n\n".join(retrieved)
