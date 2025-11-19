import os
import logging
from google import genai
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize image search tool
image_search_tool = DuckDuckGoSearchResults(
    output_format="list", backend="images", max_results=8
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_images(query: str):
    """Search for images related to the query."""
    try:
        logger.info(f"Searching for images: {query}")
        results = image_search_tool.invoke(query)
        logger.info(f"Found {len(results)} images for query: {query}")
        return results
    except Exception as e:
        logger.warning(f"Image search failed (likely rate limited): {e}")
        return []  # Return empty list so agent can continue without image results


def generate_initial_html(prompt: str):
    """
    Generates the initial HTML based on a user prompt.
    """
    # First, search for relevant images
    image_results = search_images(prompt)

    # Prepare image context for the agent
    image_context = ""
    if image_results:
        image_context = "\n\nAVAILABLE IMAGES:\n"
        for i, img in enumerate(image_results[:6]):  # Limit to 6 images
            title = img.get("title", f"Image {i + 1}")
            url = img.get("image", "")
            image_context += f"{i + 1}. {title} - {url}\n"
        image_context += (
            "\nYou can use these image URLs in your HTML with <img> tags.\n"
        )
    else:
        image_context = "\n\nNo images found for this topic. Create the HTML without images or use placeholder images.\n"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"You are creating a web interface based on the user's prompt: {prompt}. "
        "Your goal is to represent information in a visually appealing and well-structured way."
        "Therefore, focus on the content and design, you do not need traditional web page elements like headers or footers or forms."
        "You should include text but not too much, and it should be concise and relevant to the topic. "
        "Your content should include components that the user can interact with, such as buttons, selections, if necessary. "
        "You should not include JavaScript in your response, just HTML and CSS. The interactions will be handled by the agent instead. "
        f"{image_context}"
        "IMPORTANT: When using images, use the exact URLs provided above. "
        "Make sure to include alt text describing what each image shows. "
        "Do not include anything other than HTML code.",
    )

    return process_result_into_html(response.text)


def process_interaction(interaction: dict, current_html: str):
    """
    Processes a user interaction and returns a full HTML page.
    """
    action = interaction.get("action", "click")
    element_id = interaction.get("element_id")
    element_type = interaction.get("element_type", "unknown")
    value = interaction.get("value")

    # Build context-aware prompt based on interaction type
    if action == "click":
        action_desc = f"clicked on the {element_type} element with id '{element_id}'"
    elif action == "change" and value is not None:
        action_desc = f"changed the {element_type} element with id '{element_id}' to value '{value}'"
    elif action == "input" and value is not None:
        action_desc = (
            f"typed '{value}' into the {element_type} element with id '{element_id}'"
        )
    elif action == "submit":
        action_desc = f"submitted the {element_type} with id '{element_id}'"
    else:
        action_desc = f"performed action '{action}' on the {element_type} element with id '{element_id}'"

    # Add value context if available
    value_context = f" The new value is: {value}" if value else ""

    logger.info(f"Processing interaction: {action_desc}{value_context}")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"The user {action_desc}.{value_context} "
        f"Here is the previous HTML for context:\n{current_html}\n"
        "Generate a complete, updated HTML page from scratch that maintains "
        "the same design and incorporates any changes due to this interaction. "
        "Make sure to reflect the user's action appropriately in the new HTML. "
        "Try not to make changes to CSS or JavaScript unless necessary, just update HTML for most cases."
        "If you do not think any changes are needed, return the same HTML without modifications."
        "Do not include anything other than HTML code in your response.",
    )

    html = process_result_into_html(response.text)
    if html is None:
        logger.warning("Failed to process interaction, returning current HTML")
        return current_html
    else:
        logger.info(
            f"Successfully processed {action} interaction for element_id {element_id}"
        )
        return html


def process_result_into_html(result: str) -> str:
    """
    Processes the result into HTML format.
    """
    if not result:
        return "<p>Gemini is not feeling it right now...</p>"

    # Clean up the response by removing markdown code blocks
    if "```html" in result:
        start = result.find("```html") + len("```html")
        end = result.find("```", start)
        if end != -1:
            result = result[start:end].strip()
        else:
            result = result[start:].strip()

        logger.info(
            f"Processed result into HTML: {result[:100]}..."
        )  # Log first 100 chars

        if not result.strip():
            return "<p>Gemini is not feeling it right now...</p>"

        return result.strip()
    else:
        logger.warning("Response did not contain HTML code block")
        return None
