import os
from typing import Dict, List, Any
import logging
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
from langchain.schema import Document
from rag_manager import rag_manager
from google.genai import types
from google import genai

# Initialize search tools
search_tool = DuckDuckGoSearchResults(output_format="list", max_results=5)
image_search_tool = DuckDuckGoSearchResults(
    output_format="list", backend="images", max_results=8
)

# Initialize Imagen client
genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# Research tools
@tool(description="Search the web for information.")
def web_search_tool_fn(query: str) -> List[Dict[str, Any]]:
    """Search the web for information."""
    try:
        return search_tool.invoke(query)
    except Exception as e:
        logging.warning(f"Web search failed (likely rate limited): {e}")
        return []  # Return empty list so agent can continue without search results


@tool(description="Search for images related to the query.")
def image_search_tool_fn(query: str) -> List[Dict[str, Any]]:
    """Search for images related to the query."""
    try:
        return image_search_tool.invoke(query)
    except Exception as e:
        logging.warning(f"Image search failed (likely rate limited): {e}")
        return []  # Return empty list so agent can continue without image results


@tool(description="Retrieve relevant documents from the user's uploaded materials.")
def rag_search_tool_fn(query: str, user_id: str = "anonymous") -> List[Document]:
    """Retrieve relevant documents from the user's uploaded materials."""
    return rag_manager.retrieve_documents(query, user_id)


# UI agent tools
@tool(description="Search for UI inspiration images.")
def ui_image_search_tool_fn(query: str) -> List[Dict[str, Any]]:
    """Search for UI inspiration images to enhance UI design."""
    try:
        return image_search_tool.invoke(query)
    except Exception as e:
        logging.warning(f"UI image search failed (likely rate limited): {e}")
        return []  # Return empty list so agent can continue without UI images


@tool(
    description="Generate an image using Google Imagen. Limited to 1 image per request."
)
def imagen_generate_tool_fn(prompt: str) -> str:
    """Generate an image using Google Imagen. Limited to 1 image per request.

    Args:
        prompt: A detailed description of the image to generate

    Returns:
        Base64 encoded image data or error message
    """
    try:
        logging.info(f"Generating image with Imagen: {prompt}")

        response = genai_client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                include_rai_reason=True,
                output_mime_type="image/jpeg",
            ),
        )

        # Get the generated image
        generated_image = response.generated_images[0].image

        img_data_url = f"data:image/jpeg;base64,{generated_image.image_bytes}"

        logging.info("Image generated successfully")
        return img_data_url

    except Exception as e:
        logging.error(f"Error generating image with Imagen: {e}")
        return f"Error generating image: {str(e)}"


# Tool lists for different agents
research_tools = [web_search_tool_fn, image_search_tool_fn, rag_search_tool_fn]
ui_tools = [
    ui_image_search_tool_fn
]  # Removed imagen_generate_tool_fn to prevent token overflow
