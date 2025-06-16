import os
from typing import Dict, List, Any, TypedDict, Annotated, Literal
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, AIMessage
from langchain_core.messages import BaseMessage
import json
import asyncio
import operator

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# Initialize search tools
search_tool = DuckDuckGoSearchResults(output_format="list", max_results=5)
image_search_tool = DuckDuckGoSearchResults(
    output_format="list", backend="images", max_results=8
)


# Define the state structure with routing path
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    prompt: str
    search_results: List[Dict]
    image_results: List[Dict]
    final_ui: Dict[str, Any]
    decision_path: Literal[
        "search_and_images", "search_only", "images_only", "ui_generator"
    ]


# Decision Agent - Returns routing decision
async def decision_agent_node(state: AgentState):
    """Agent that decides the routing path based on what's needed"""
    logging.info("Decision agent analyzing prompt")
    prompt = state["prompt"]

    decision_prompt = f"""Analyze this user prompt and decide the best path:

USER PROMPT: "{prompt}"

Consider these guidelines:
- SEARCH is needed for: current events, detailed information, recent developments, factual research, news, statistics, complex topics needing external data
- SEARCH is NOT needed for: simple factual questions the LLM knows, basic definitions, general knowledge, simple math, obvious answers
- IMAGES are needed for: visual content, galleries, portfolios, products, places, people, things that benefit from visual representation
- IMAGES are NOT needed for: text-heavy content, lists, pure information, abstract concepts, technical documentation

Based on what's needed, choose the best path:
- "search_and_images" - if both search and images are needed
- "search_only" - if only search is needed
- "images_only" - if only images are needed
- "ui_generator" - if neither search nor images are needed (use LLM knowledge directly)

Examples:
- "What are two countries in North America?" → "images_only" (simple question, but images helpful)
- "Write a blog about climate change" → "search_only" (needs recent data, mostly text)  
- "Show me modern architecture" → "search_and_images" (needs current examples + visuals)
- "What is 2+2?" → "ui_generator" (simple math, no external data needed)

Return ONLY a JSON object:
{{
    "path": "search_and_images|search_only|images_only|ui_generator",
    "reasoning": "brief explanation"
}}"""

    try:
        response = llm.invoke([HumanMessage(content=decision_prompt)])
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        decision = json.loads(content)
        path = decision.get("path", "search_and_images")  # Safe default

        return {
            **state,
            "decision_path": path,
            "messages": state["messages"]
            + [
                AIMessage(content=f"Decision: {path} - {decision.get('reasoning', '')}")
            ],
        }

    except Exception as e:
        logging.error(f"Decision agent error: {e}")
        # Default to safe fallback
        return {
            **state,
            "decision_path": "search_and_images",
            "messages": state["messages"]
            + [AIMessage(content=f"Decision agent failed, using fallback: {str(e)}")],
        }


# Search Agent
async def search_agent_node(state: AgentState):
    """Agent responsible for searching content"""
    logging.info("Search agent processing request")
    prompt = state["prompt"]

    try:
        search_results = search_tool.invoke(prompt)
        return {
            **state,
            "search_results": search_results,
            "messages": state["messages"]
            + [AIMessage(content=f"Found {len(search_results)} search results")],
        }

    except Exception as e:
        logging.error(f"Search agent error: {e}")
        return {
            **state,
            "search_results": [],
            "messages": state["messages"]
            + [AIMessage(content=f"Search failed: {str(e)}")],
        }


# Image Agent
async def image_agent_node(state: AgentState):
    """Agent responsible for finding images"""
    logging.info("Image agent processing request")
    prompt = state["prompt"]

    try:
        image_results = image_search_tool.invoke(prompt)
        return {
            **state,
            "image_results": image_results,
            "messages": state["messages"]
            + [AIMessage(content=f"Found {len(image_results)} image results")],
        }

    except Exception as e:
        logging.error(f"Image agent error: {e}")
        return {
            **state,
            "image_results": [],
            "messages": state["messages"]
            + [AIMessage(content=f"Image search failed: {str(e)}")],
        }


# Combined Search and Images Node
async def search_and_images_node(state: AgentState):
    """Agent that handles both search and images in parallel"""
    logging.info("Processing search and images in parallel")
    prompt = state["prompt"]

    try:
        # Run both search and images in parallel
        search_task = asyncio.create_task(asyncio.to_thread(search_tool.invoke, prompt))
        image_task = asyncio.create_task(
            asyncio.to_thread(image_search_tool.invoke, prompt)
        )

        search_results, image_results = await asyncio.gather(
            search_task, image_task, return_exceptions=True
        )

        # Handle potential exceptions
        if isinstance(search_results, Exception):
            logging.error(f"Search error: {search_results}")
            search_results = []

        if isinstance(image_results, Exception):
            logging.error(f"Image error: {image_results}")
            image_results = []

        return {
            **state,
            "search_results": search_results,
            "image_results": image_results,
            "messages": state["messages"]
            + [
                AIMessage(
                    content=f"Found {len(search_results)} search results and {len(image_results)} images"
                )
            ],
        }

    except Exception as e:
        logging.error(f"Combined search and images error: {e}")
        return {
            **state,
            "search_results": [],
            "image_results": [],
            "messages": state["messages"]
            + [AIMessage(content=f"Search and images failed: {str(e)}")],
        }


# UI Generator - Creates components based on available data
async def ui_generator_node(state: AgentState):
    """Generate UI components based on prompt and available data"""
    logging.info("UI generator creating components")

    prompt = state["prompt"]
    search_results = state.get("search_results", [])
    image_results = state.get("image_results", [])

    # Prepare context for UI generation
    search_context = ""
    if search_results:
        for i, result in enumerate(search_results[:5]):
            search_context += f"Result {i + 1}: Title: {result.get('title', '')}, Snippet: {result.get('snippet', '')}\n"

    image_context = ""
    if image_results:
        for i, img in enumerate(image_results[:6]):
            image_context += (
                f"Image {i + 1}: {img.get('title', '')} - {img.get('image', '')}\n"
            )

    ui_prompt = f"""You are a UI/UX expert creating beautiful, diverse user interfaces. Always aim for variety and visual interest!

AVAILABLE COMPONENTS (use diverse combinations):
1. **hero** - Large featured banner with background image, title, subtitle, and call-to-action button
   → Best for: Main topics, landing sections, featured content
2. **card** - Information display with title, content, optional image and badge
   → Best for: Individual items, articles, products, detailed info
3. **gallery** - Grid of images with captions
   → Best for: Visual collections, portfolios, examples, showcases
4. **list** - Organized items with icons and descriptions
   → Best for: Steps, features, comparisons, structured data
5. **stats** - Numerical data display with icons and labels
   → Best for: Metrics, achievements, data points, analytics
6. **testimonial** - Quote display with author information and avatar
   → Best for: Reviews, quotes, user feedback, expert opinions

USER PROMPT: "{prompt}"

SEARCH RESULTS:
{search_context if search_context else "No search results available - use your knowledge"}

AVAILABLE IMAGES:
{image_context if image_context else "No images available"}

DIVERSITY REQUIREMENTS:
- ALWAYS use at least 3 different component types
- Mix visual (hero, gallery) with informational (card, list) components
- Include interactive elements when possible (stats, testimonials)
- Vary the content structure and visual hierarchy
- Create a cohesive but diverse user experience

INSTRUCTIONS:
1. Create 3-5 components using DIFFERENT types for visual variety
2. Start with a hero or gallery if the topic is visual
3. Include stats or testimonials to add credibility and engagement
4. Use lists for structured information and cards for detailed content
5. Make titles concise (max 60 chars) and content readable (max 200 chars for cards)
6. Ensure each component serves a unique purpose in the overall experience

Return ONLY a valid JSON object:
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
hero: {{"title": "string", "subtitle": "string", "image": "url_or_empty", "buttonText": "string", "buttonLink": "url_or_empty"}}
card: {{"title": "string", "content": "string", "image": "url_or_empty", "badge": "string_or_empty"}}
gallery: {{"title": "string", "images": [{{"url": "string", "caption": "string"}}]}}
list: {{"title": "string", "items": [{{"text": "string", "icon": "emoji"}}]}}
stats: {{"title": "string", "data": [{{"value": "string", "label": "string", "icon": "emoji"}}]}}
testimonial: {{"quote": "string", "author": "string", "role": "string", "avatar": "url_or_empty"}}

An example is given below:

{{
    "components": [
        {{
            "type": "gallery",
            "props": {{
                "title": "My Gallery",
                "images": [
                    {{"url": "https://example.com/image1.jpg", "caption": "Image 1"}},
                    {{"url": "https://example.com/image2.jpg", "caption": "Image 2"}}
                ]
            }}
        }}
    ]
}}
"""

    try:
        response = llm.invoke([HumanMessage(content=ui_prompt)])
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        ui_components = json.loads(content)

        return {
            **state,
            "final_ui": ui_components,
            "messages": state["messages"]
            + [AIMessage(content="UI components generated successfully")],
        }

    except Exception as e:
        logging.error(f"UI generator error: {e}")
        # Fallback UI
        fallback_ui = {
            "components": [
                {
                    "type": "card",
                    "props": {
                        "title": "Response",
                        "content": "Still trying to wrap GPT? Go touch some grass bro... How long havn't you showered btw?",
                        "badge": "Generated",
                    },
                }
            ]
        }
        return {
            **state,
            "final_ui": fallback_ui,
            "messages": state["messages"]
            + [AIMessage(content=f"UI generation failed, using fallback: {str(e)}")],
        }


# Routing function for the decision agent, simply returns the decision path in the state
def route_decision(
    state: AgentState,
) -> Literal["search_and_images", "search_only", "images_only", "ui_generator"]:
    """Route based on the decision agent's choice"""
    decision_path = state.get("decision_path", "ui_generator")
    logging.info(f"Routing to: {decision_path}")
    return decision_path


# Create the graph-based workflow with conditional routing
def create_graph_workflow():
    """Create a graph workflow with natural conditional routing"""
    workflow = StateGraph(AgentState)

    # Add nodes (no separate direct_ui node needed)
    workflow.add_node("decision", decision_agent_node)
    workflow.add_node("search_and_images", search_and_images_node)
    workflow.add_node("search_only", search_agent_node)
    workflow.add_node("images_only", image_agent_node)
    workflow.add_node("ui_generator", ui_generator_node)

    # Set entry point
    workflow.set_entry_point("decision")

    # Add conditional edges from decision agent
    workflow.add_conditional_edges(
        "decision",
        route_decision,
        {
            "search_and_images": "search_and_images",
            "search_only": "search_only",
            "images_only": "images_only",
            "ui_generator": "ui_generator",
        },
    )

    # Paths that gather data lead to ui_generator
    workflow.add_edge("search_and_images", "ui_generator")
    workflow.add_edge("search_only", "ui_generator")
    workflow.add_edge("images_only", "ui_generator")

    # Final edge to END
    workflow.add_edge("ui_generator", END)

    return workflow.compile()


# Create the compiled workflow
graph_workflow = create_graph_workflow()


async def process_prompt(prompt: str) -> Dict[str, Any]:
    """Main function to process a prompt using the graph-based workflow"""
    logging.info(f"Processing prompt with graph workflow: {prompt}")

    try:
        # Initialize the state
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "prompt": prompt,
            "search_results": [],
            "image_results": [],
            "final_ui": {},
        }

        # Run the workflow
        result = await graph_workflow.ainvoke(initial_state)

        logging.info("Graph workflow completed successfully")
        return result["final_ui"]

    except Exception as e:
        logging.exception("Error in graph workflow:")
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
