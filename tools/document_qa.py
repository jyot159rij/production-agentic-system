import os
import chromadb
from sentence_transformers import SentenceTransformer
from tools.base import BaseTool

class DocumentQATool(BaseTool):
    name = "document_qa"
    description = "Answer questions from internal documents. Input: question as string."

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.client.get_or_create_collection("documents")
        self._index_docs()

    def _index_docs(self):
        docs_folder = "docs"
        if not os.path.exists(docs_folder):
            return
        for filename in os.listdir(docs_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(docs_folder, filename)
                with open(filepath, "r") as f:
                    content = f.read()
                doc_id = filename.replace(".txt", "")
                existing = self.collection.get(ids=[doc_id])
                if not existing["ids"]:
                    embedding = self.model.encode(content).tolist()
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[content],
                        metadatas=[{"filename": filename}]
                    )

    def run(self, question: str) -> str:
        try:
            embedding = self.model.encode(question).tolist()
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=2
            )
            if not results["documents"][0]:
                return "No relevant documents found."
            return "\n---\n".join(results["documents"][0])
        except Exception as e:
            return f"Document QA error: {str(e)}"