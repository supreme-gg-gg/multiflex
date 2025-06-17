import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
)

logger = logging.getLogger(__name__)

load_dotenv()


class RAGManager:
    """Simplified RAG manager using LangChain community components."""

    def __init__(self):
        # Initialize embeddings

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

        # Initialize LLM for routing and grading
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        # TODO: In production, use persistent storage for vectorstore
        # For now, create in-memory vectorstore that will be recreated on restart
        self.vectorstore = None
        self.retriever = None

        # Initialize retrieval grader
        self.retrieval_grader_prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question. 
            If the document contains information related to the user question, grade it as relevant. 
            The goal is to filter out erroneous retrievals.
            
            Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question.
            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
            
            Here is the retrieved document: {document}
            Here is the user question: {question}""",
            input_variables=["question", "document"],
        )

        self.retrieval_grader = (
            self.retrieval_grader_prompt | self.llm | JsonOutputParser()
        )

    def load_document(
        self, file_path: str, filename: str, user_id: str
    ) -> List[Document]:
        """Load and process a single document."""
        try:
            file_ext = Path(filename).suffix.lower()

            # Choose appropriate loader based on file type
            if file_ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_ext == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif file_ext == ".docx":
                loader = UnstructuredWordDocumentLoader(file_path)
            elif file_ext == ".pptx":
                loader = UnstructuredPowerPointLoader(file_path)
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return []

            # Load documents
            documents = loader.load()

            # Add metadata
            for doc in documents:
                doc.metadata.update(
                    {"user_id": user_id, "filename": filename, "file_type": file_ext}
                )

            # Split documents
            doc_splits = self.text_splitter.split_documents(documents)

            logger.info(f"Loaded {filename}: {len(doc_splits)} chunks created")
            return doc_splits

        except Exception as e:
            logger.error(f"Error loading document {filename}: {str(e)}")
            return []

    def add_documents_to_vectorstore(self, documents: List[Document]) -> bool:
        """Add documents to the vectorstore."""
        try:
            if not documents:
                return False

            if self.vectorstore is None:
                # Create new vectorstore
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection_name="educational_materials",
                    persist_directory="./vectorstore_data",
                )
            else:
                # Add to existing vectorstore
                self.vectorstore.add_documents(documents)

            # Update retriever
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

            logger.info(f"Added {len(documents)} documents to vectorstore")
            return True

        except Exception as e:
            logger.error(f"Error adding documents to vectorstore: {str(e)}")
            return False

    def retrieve_documents(
        self, question: str, user_id: Optional[str] = None
    ) -> List[Document]:
        """Retrieve relevant documents for the question."""
        try:
            if self.retriever is None:
                return []

            # Retrieve documents
            docs = self.retriever.invoke(question)

            # Filter by user_id if provided
            if user_id:
                docs = [doc for doc in docs if doc.metadata.get("user_id") == user_id]

            # Grade retrieved documents for relevance
            relevant_docs = []
            for doc in docs:
                try:
                    grade = self.retrieval_grader.invoke(
                        {"question": question, "document": doc.page_content}
                    )

                    if grade.get("score") == "yes":
                        relevant_docs.append(doc)
                except Exception as e:
                    logger.warning(f"Error grading document: {str(e)}")
                    # Include document if grading fails
                    relevant_docs.append(doc)

            logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []

    def format_docs(self, docs: List[Document]) -> str:
        """Format documents for context."""
        if not docs:
            return ""

        formatted_docs = []
        for i, doc in enumerate(docs):
            filename = doc.metadata.get("filename", "Unknown")
            content = doc.page_content
            formatted_docs.append(f"Document {i + 1} ({filename}):\n{content}")

        return "\n\n".join(formatted_docs)

    def get_user_documents_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about user's documents."""
        try:
            if self.vectorstore is None:
                return {"total_documents": 0, "files": []}

            # Get all documents for user (this is a simplified approach)
            # TODO: In production, store document metadata separately for efficient querying
            all_docs = self.vectorstore.get()

            user_docs = []
            files = set()

            for i, metadata in enumerate(all_docs.get("metadatas", [])):
                if metadata.get("user_id") == user_id:
                    user_docs.append(metadata)
                    files.add(metadata.get("filename", "Unknown"))

            return {
                "total_documents": len(user_docs),
                "total_chunks": len(user_docs),
                "files": list(files),
                "file_count": len(files),
            }

        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            return {"error": str(e)}

    def clear_vectorstore(self):
        """Clear the vectorstore (for development purposes)."""
        # TODO: In production, implement proper document deletion by user_id
        self.vectorstore = None
        self.retriever = None
        logger.info("Vectorstore cleared")


# Global instance
rag_manager = RAGManager()
