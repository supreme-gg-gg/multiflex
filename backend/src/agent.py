import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage
import json
import asyncio

load_dotenv()

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# Initialize search tools
search_tool = DuckDuckGoSearchResults(output_format="list", max_results=5)

image_search_tool = DuckDuckGoSearchResults(
    output_format="list", backend="images", max_results=8
)

# Create the agent with tools
tools = [search_tool, image_search_tool]
agent = create_react_agent(model=llm, tools=tools)


def create_ui_with_ai(
    search_results: List[Dict], image_results: List[Dict], prompt: str
) -> Dict[str, Any]:
    """Use AI to intelligently choose the best UI components based on search results"""

    try:
        # Prepare context for AI decision making
        search_context = ""
        for i, result in enumerate(search_results[:5]):
            search_context += f"Result {i + 1}: Title: {result.get('title', '')}, Snippet: {result.get('snippet', '')}\n"

        image_context = ""
        for i, img in enumerate(image_results[:6]):
            image_context += (
                f"Image {i + 1}: {img.get('title', '')} - {img.get('image', '')}\n"
            )

        # AI prompt for intelligent UI component selection
        ai_prompt = f"""You are a UI/UX expert that creates beautiful, relevant user interfaces based on search results. 

AVAILABLE COMPONENTS:
1. **hero** - Large featured banner with background image, title, subtitle, and call-to-action button
   Use for: Main topics, featured content, breaking news, important announcements
   
2. **card** - Information display with title, content, optional image and badge
   Use for: Individual articles, products, services, detailed information pieces
   
3. **gallery** - Grid of images with captions
   Use for: Multiple related images, portfolios, collections, visual content
   
4. **list** - Organized items with icons and descriptions
   Use for: Step-by-step guides, features, comparisons, structured information
   
5. **stats** - Numerical data display with icons and labels
   Use for: Analytics, metrics, achievements, quantitative information
   
6. **testimonial** - Quote display with author information and avatar
   Use for: Reviews, quotes, opinions, personal stories

USER PROMPT: "{prompt}"

SEARCH RESULTS:
{search_context}

AVAILABLE IMAGES:
{image_context}

INSTRUCTIONS:
1. Analyze the user's prompt and search results
2. Choose 2-4 appropriate components that best present this information
3. Create engaging, relevant content for each component
4. Use the most suitable images for each component
5. Make titles concise but descriptive (max 60 chars)
6. Keep content informative but readable (max 200 chars for cards)
7. Add relevant badges/icons where appropriate

Return ONLY a valid JSON object with this exact structure:
{{
    "components": [
        {{
            "type": "component_name",
            "props": {{
                // component-specific properties
            }}
        }}
    ]
}}

COMPONENT SPECIFICATIONS:

hero: {{"title": "string", "subtitle": "string", "image": "url", "buttonText": "string", "buttonLink": "url"}}
card: {{"title": "string", "content": "string", "image": "url", "badge": "string"}}
gallery: {{"title": "string", "images": [{{"url": "string", "caption": "string"}}]}}
list: {{"title": "string", "items": [{{"text": "string", "icon": "emoji"}}]}}
stats: {{"title": "string", "data": [{{"value": "string", "label": "string", "icon": "emoji"}}]}}
testimonial: {{"quote": "string", "author": "string", "role": "string", "avatar": "url"}}

Choose components that best match the content type and user intent. Be creative but relevant!"""

        # Get AI response for UI component selection
        ai_response = llm.invoke([HumanMessage(content=ai_prompt)])

        # Parse AI response
        try:
            content = ai_response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            ui_spec = json.loads(content)
            return ui_spec

        except json.JSONDecodeError:
            # Fallback if AI response parsing fails
            return create_fallback_ui(search_results, image_results, prompt)

    except Exception as e:
        print(f"AI UI creation error: {e}")
        return create_fallback_ui(search_results, image_results, prompt)


def create_fallback_ui(
    search_results: List[Dict], image_results: List[Dict], prompt: str
) -> Dict[str, Any]:
    """Fallback UI creation if AI fails"""
    components = []

    # Hero component with first image
    if image_results and search_results:
        components.append(
            {
                "type": "hero",
                "props": {
                    "title": search_results[0].get("title", prompt)[:60],
                    "subtitle": search_results[0].get("snippet", "")[:120],
                    "image": image_results[0].get("image", ""),
                    "buttonText": "Learn More",
                    "buttonLink": search_results[0].get("link", "#"),
                },
            }
        )

    # Gallery if we have multiple images
    if len(image_results) > 1:
        gallery_images = []
        for img in image_results[1:4]:
            gallery_images.append(
                {"url": img.get("image", ""), "caption": img.get("title", "")[:50]}
            )

        components.append(
            {
                "type": "gallery",
                "props": {"title": f"Images: {prompt}", "images": gallery_images},
            }
        )

    # Cards for additional content
    for i, result in enumerate(search_results[1:3]):
        img_url = (
            image_results[i + 4].get("image", "")
            if i + 4 < len(image_results)
            else None
        )
        components.append(
            {
                "type": "card",
                "props": {
                    "title": result.get("title", "")[:80],
                    "content": result.get("snippet", "")[:200],
                    "image": img_url,
                    "badge": "Search Result",
                },
            }
        )

    return {"components": components}


async def process_prompt(prompt: str) -> Dict[str, Any]:
    """Main function to process a prompt and return UI components"""
    try:
        # Search for general content
        content_message = f"Search for comprehensive information about: {prompt}"
        content_result = await agent.ainvoke(
            {
                "messages": [
                    ("user", f"Use DuckDuckGoSearchResults to {content_message}")
                ]
            }
        )

        # Search for images
        image_message = f"Search for relevant images about: {prompt}"
        image_result = await agent.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        f"Use DuckDuckGoSearchResults with backend='images' to {image_message}",
                    )
                ]
            }
        )

        # Extract search results from agent responses
        content_search_results = []
        image_search_results = []

        # Parse the agent responses to extract actual search results
        for message in content_result["messages"]:
            if hasattr(message, "content") and isinstance(message.content, str):
                if "[{" in message.content and "}]" in message.content:
                    try:
                        start = message.content.find("[{")
                        end = message.content.rfind("}]") + 2
                        json_str = message.content[start:end]
                        content_search_results = json.loads(json_str)
                        break
                    except:
                        continue

        for message in image_result["messages"]:
            if hasattr(message, "content") and isinstance(message.content, str):
                if "[{" in message.content and "}]" in message.content:
                    try:
                        start = message.content.find("[{")
                        end = message.content.rfind("}]") + 2
                        json_str = message.content[start:end]
                        image_search_results = json.loads(json_str)
                        break
                    except:
                        continue

        # Fallback: use the tools directly if agent parsing fails
        if not content_search_results:
            content_search_results = search_tool.invoke(prompt)

        if not image_search_results:
            image_search_results = image_search_tool.invoke(prompt)

        # Use AI to intelligently create UI components
        ui_response = create_ui_with_ai(
            content_search_results, image_search_results, prompt
        )

        return ui_response

    except Exception as e:
        return {
            "components": [
                {
                    "type": "card",
                    "props": {
                        "title": "Error",
                        "content": f"An error occurred while processing your request: {str(e)}",
                        "badge": "Error",
                    },
                }
            ],
            "error": str(e),
        }
