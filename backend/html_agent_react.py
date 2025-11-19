import os
import logging
import uuid
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import research_tools
from css_templates import inject_css_into_html

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the LLM
model = ChatGoogleGenerativeAI(
    # model="gemini-2.5-flash-lite-preview-06-17",
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

# Create checkpointer for memory
checkpointer = InMemorySaver()

# Create the ReAct agent with tools
html_agent = create_react_agent(
    model=model,
    tools=research_tools,
    checkpointer=checkpointer,
    prompt="""You are an intelligent HTML creation agent that generates complete, well-structured HTML pages.
    You should try to make visually appealing and well structured HTML that uses various HTML elements to aid comprehension.
    Avoid using excessive text without structure or images such as galleries, tables, lists, etc.

Your capabilities:
1. Use web_search_tool_fn to search for current information about topics
2. Use image_search_tool_fn to find relevant images for the content
3. Use rag_search_tool_fn to retrieve relevant documents from uploaded materials

CRITICAL HTML GENERATION RULES:
1. ALWAYS generate valid HTML with proper tags: <div>, <h1>, <h2>, <p>, <img>, <section>, etc.
2. NEVER return plain text - everything must be wrapped in HTML tags
3. Use semantic HTML structure with proper headings (h1, h2, h3)
4. Create engaging content with multiple sections
5. Include images with proper <img> tags and alt text
6. Do NOT include <style> tags, <html>, <head>, or <body> tags - just the content

EXAMPLE GOOD OUTPUT:
<div>
  <h1>About Our Company</h1>
  <p>This is a paragraph describing the company.</p>
  <h2>Our Mission</h2>
  <p>Another paragraph about mission.</p>
  <img src="https://example.com/image.jpg" alt="Company photo" />
</div>

EXAMPLE BAD OUTPUT:
About Our Company
This is just plain text without HTML tags.

For follow-up requests:
- Maintain the HTML structure and add/modify content appropriately
- Use tools if you need additional information

Return ONLY the HTML content inside proper HTML tags (no markdown, no explanations).
""",
)


async def process_html_request(
    prompt: str, user_id: str = "anonymous", session_id: str = None
) -> Dict[str, Any]:
    """Process a request to generate HTML using ReAct agent."""
    logger.info(f"Processing HTML request: {prompt}")

    try:
        # Use session_id or generate one for this conversation
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Create config for the agent with thread_id for memory
        config = {"configurable": {"thread_id": session_id}}

        # Stream the agent execution for debugging
        logger.info("=== Starting ReAct Agent Execution ===")
        final_response = None

        async for step in html_agent.astream(
            {"messages": [{"role": "user", "content": prompt}]},
            config,
            stream_mode="values",
        ):
            if step and "messages" in step:
                last_message = step["messages"][-1]
                logger.info(f"Agent Step: {last_message}")
                final_response = step

        logger.info("=== ReAct Agent Execution Complete ===")

        # Extract HTML content from the response
        html_content = ""
        if final_response and "messages" in final_response:
            # Get the last assistant message
            for message in reversed(final_response["messages"]):
                if hasattr(message, "content") and message.content:
                    html_content = message.content
                    break

        logger.info(f"Raw HTML content: {html_content[:200]}...")

        # Clean up the HTML content
        if html_content:
            # Remove markdown code blocks if present
            cleaned_html = html_content
            if "```html" in cleaned_html:
                start = cleaned_html.find("```html") + len("```html")
                end = cleaned_html.find("```", start)
                if end != -1:
                    cleaned_html = cleaned_html[start:end].strip()
                else:
                    cleaned_html = cleaned_html[start:].strip()
            elif "```" in cleaned_html:
                # Remove any other code blocks
                lines = cleaned_html.split("\n")
                cleaned_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if not in_code_block:
                        cleaned_lines.append(line)
                cleaned_html = "\n".join(cleaned_lines)

            logger.info(f"Cleaned HTML content: {cleaned_html[:200]}...")

            # Inject consistent CSS styling - this is crucial for proper styling
            final_html = inject_css_into_html(cleaned_html)

            logger.info(f"Final HTML with CSS ({len(final_html)} characters)")

            return {
                "html_content": final_html,
                "session_id": session_id,
                "success": True,
            }
        else:
            # Fallback if no content generated
            fallback_html = """
            <div class="response-card">
                <h2>Content Generated</h2>
                <p>I've processed your request but wasn't able to generate HTML content.</p>
                <p>Please try rephrasing your request.</p>
            </div>
            """
            final_html = inject_css_into_html(fallback_html)

            return {
                "html_content": final_html,
                "session_id": session_id,
                "success": True,
            }

    except Exception as e:
        logger.exception("Error in HTML agent processing:")
        error_html = f"""
        <div class="response-card">
            <h2>Error</h2>
            <p>An error occurred while generating the HTML: {str(e)}</p>
            <p>Please try again with a different request.</p>
        </div>
        """
        final_html = inject_css_into_html(error_html)

        return {
            "html_content": final_html,
            "session_id": session_id or "error",
            "success": False,
            "error": str(e),
        }


async def process_followup_request(
    followup_prompt: str, session_id: str, current_html: str, user_id: str = "anonymous"
) -> Dict[str, Any]:
    """Process a follow-up request to modify existing HTML."""
    logger.info(f"Processing follow-up request: {followup_prompt}")

    try:
        # Create config for the agent with thread_id for memory continuity
        config = {"configurable": {"thread_id": session_id}}

        # Stream the follow-up execution for debugging
        logger.info("=== Starting Follow-up ReAct Agent Execution ===")
        final_response = None

        async for step in html_agent.astream(
            {"messages": [{"role": "user", "content": followup_prompt}]},
            config,
            stream_mode="values",
        ):
            if step and "messages" in step:
                last_message = step["messages"][-1]
                logger.info(f"Follow-up Agent Step: {last_message}")
                final_response = step

        logger.info("=== Follow-up ReAct Agent Execution Complete ===")

        # Extract HTML content from the response
        html_content = ""
        if final_response and "messages" in final_response:
            # Get the last assistant message
            for message in reversed(final_response["messages"]):
                if hasattr(message, "content") and message.content:
                    html_content = message.content
                    break

        if html_content:
            # Clean up and process the HTML
            cleaned_html = html_content
            if "```html" in cleaned_html:
                start = cleaned_html.find("```html") + len("```html")
                end = cleaned_html.find("```", start)
                if end != -1:
                    cleaned_html = cleaned_html[start:end].strip()
                else:
                    cleaned_html = cleaned_html[start:].strip()
            elif "```" in cleaned_html:
                lines = cleaned_html.split("\n")
                cleaned_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if not in_code_block:
                        cleaned_lines.append(line)
                cleaned_html = "\n".join(cleaned_lines)

            # Inject consistent CSS styling
            final_html = inject_css_into_html(cleaned_html)

            return {
                "html_content": final_html,
                "session_id": session_id,
                "success": True,
            }
        else:
            # Return current HTML if no new content generated
            return {
                "html_content": current_html,
                "session_id": session_id,
                "success": True,
            }

    except Exception as e:
        logger.exception("Error in follow-up processing:")
        return {
            "html_content": current_html,  # Return current HTML if follow-up fails
            "session_id": session_id,
            "success": False,
            "error": str(e),
        }
