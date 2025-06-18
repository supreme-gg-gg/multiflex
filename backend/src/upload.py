"""File upload endpoints for educational materials."""

import os
import tempfile
import logging
from typing import List
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from rag_manager import rag_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...), user_id: str = Form(...)
):
    """Upload and process educational documents."""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    results = []
    all_documents = []

    for file in files:
        try:
            # Validate file
            if not file.filename:
                results.append(
                    {
                        "filename": "unknown",
                        "status": "error",
                        "message": "No filename provided",
                    }
                )
                continue

            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in SUPPORTED_EXTENSIONS:
                results.append(
                    {
                        "filename": file.filename,
                        "status": "error",
                        "message": f"Unsupported file type. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
                    }
                )
                continue

            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                results.append(
                    {
                        "filename": file.filename,
                        "status": "error",
                        "message": f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
                    }
                )
                continue

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name

            try:
                # Process document using simplified RAG manager
                documents = rag_manager.load_document(
                    file_path=tmp_file_path, filename=file.filename, user_id=user_id
                )

                if not documents:
                    results.append(
                        {
                            "filename": file.filename,
                            "status": "error",
                            "message": "Failed to extract text from document",
                        }
                    )
                    continue

                # Collect documents to add to vectorstore
                all_documents.extend(documents)

                results.append(
                    {
                        "filename": file.filename,
                        "status": "success",
                        "message": f"Processed into {len(documents)} chunks",
                        "chunks_created": len(documents),
                    }
                )

            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)

        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            results.append(
                {
                    "filename": file.filename,
                    "status": "error",
                    "message": f"Processing failed: {str(e)}",
                }
            )

    # Add all documents to vectorstore at once
    if all_documents:
        success = rag_manager.add_documents_to_vectorstore(all_documents)
        if not success:
            logger.error("Failed to add documents to vectorstore")

    # Count successful uploads
    successful = sum(1 for r in results if r["status"] == "success")

    return JSONResponse(
        {
            "message": f"Processed {successful}/{len(files)} files successfully",
            "results": results,
            "user_id": user_id,
            "total_chunks": len(all_documents),
        }
    )


@router.get("/documents/{user_id}")
async def get_user_documents(user_id: str):
    """Get all documents for a user."""
    try:
        doc_info = rag_manager.get_user_documents_info(user_id)

        return JSONResponse({"user_id": user_id, "statistics": doc_info})

    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{user_id}")
async def delete_user_documents(user_id: str):
    """Delete all documents (for development - clears entire vectorstore)."""
    try:
        rag_manager.clear_vectorstore()

        return JSONResponse(
            {"message": f"Cleared vectorstore (development mode)", "user_id": user_id}
        )

    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-rag")
async def test_rag_retrieval(query: str = Form(...), user_id: str = Form(...)):
    """Test RAG retrieval for a query."""
    try:
        # Check if RAG should be used
        rag_decision = rag_manager.should_use_rag(query)

        documents = []
        context = ""

        if rag_decision["use_rag"]:
            # Retrieve relevant documents
            documents = rag_manager.retrieve_documents(query, user_id)
            context = rag_manager.format_docs(documents)

        return JSONResponse(
            {
                "query": query,
                "user_id": user_id,
                "rag_decision": rag_decision,
                "retrieved_documents": len(documents),
                "context_length": len(context),
                "context_preview": context[:500] + "..."
                if len(context) > 500
                else context,
            }
        )

    except Exception as e:
        logger.error(f"Error testing RAG retrieval: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectorstore/info")
async def get_vectorstore_info():
    """Get information about the vectorstore."""
    try:
        has_vectorstore = rag_manager.vectorstore is not None

        info = {
            "has_vectorstore": has_vectorstore,
            "retriever_available": rag_manager.retriever is not None,
        }

        if has_vectorstore:
            try:
                collection_info = rag_manager.vectorstore.get()
                info["total_documents"] = len(collection_info.get("ids", []))
            except:
                info["total_documents"] = "unknown"

        return JSONResponse(info)

    except Exception as e:
        logger.error(f"Error getting vectorstore info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
