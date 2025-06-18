# filepath: /Users/supremegg/Documents/GitHub/nus-hacks/backend/src/agent.py
import os
from typing import Dict, List, Any, TypedDict, Annotated
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, AIMessage, Document
from langchain_core.messages import BaseMessage, ToolMessage
import json
import operator
import random
from tools import (
    research_tools,
    ui_tools,
    web_search_tool_fn,
    image_search_tool_fn,
    rag_search_tool_fn,
    ui_image_search_tool_fn,
    imagen_generate_tool_fn,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Initialize the LLMs
research_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

ui_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.9,  # Higher creativity for UI generation
)

# Bind tools to respective LLMs
research_llm_with_tools = research_llm.bind_tools(research_tools)
ui_llm_with_tools = ui_llm.bind_tools(ui_tools)


# Define knowledge container
class KnowledgeState(TypedDict):
    docs: List[Document]
    search: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    ui_images: List[Dict[str, Any]]
    generated_images: Dict[str, str]  # prompt -> image_data mapping


# Define the state structure
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    ui_messages: Annotated[List[BaseMessage], operator.add]
    prompt: str
    knowledge: KnowledgeState
    design_plan: str  # Creative design plan from UI Designer
    final_ui: Dict[str, Any]
    user_id: str
    iteration_count: int


# Custom tool node that updates knowledge state
def custom_tool_node(state: AgentState) -> Dict[str, Any]:
    """Execute tools and update knowledge state."""
    # Initialize knowledge if not present
    if "knowledge" not in state:
        state["knowledge"] = {
            "docs": [],
            "search": [],
            "images": [],
            "ui_images": [],
            "generated_images": {},
        }

    # Get the last message (should contain tool calls)
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_outputs = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Execute the tool
            if tool_name == "web_search_tool_fn":
                result = web_search_tool_fn.invoke(tool_args)
                state["knowledge"]["search"].extend(result)
            elif tool_name == "image_search_tool_fn":
                result = image_search_tool_fn.invoke(tool_args)
                state["knowledge"]["images"].extend(result)
            elif tool_name == "rag_search_tool_fn":
                result = rag_search_tool_fn.invoke(tool_args)
                state["knowledge"]["docs"].extend(result)

            logging.info(
                f"Tool '{tool_name}' executed with args: {tool_args}, result length: {len(result) if isinstance(result, list) else 'N/A'}"
            )

            # Create tool message
            tool_outputs.append(
                ToolMessage(
                    content=str(result),
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            **state,
            "messages": state["messages"] + tool_outputs,
        }

    return state


# UI tool node that updates UI-specific knowledge
def ui_tool_node(state: AgentState) -> Dict[str, Any]:
    """Execute UI tools and update knowledge state."""
    # Initialize knowledge if not present
    if "knowledge" not in state:
        state["knowledge"] = {
            "docs": [],
            "search": [],
            "images": [],
            "ui_images": [],
            "generated_images": {},
        }

    # Get the last UI message (should contain tool calls)
    last_message = state["ui_messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_outputs = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Execute the tool
            if tool_name == "ui_image_search_tool_fn":
                result = ui_image_search_tool_fn.invoke(tool_args)
                state["knowledge"]["ui_images"].extend(result)
            elif tool_name == "imagen_generate_tool_fn":
                # result = imagen_generate_tool_fn.invoke(tool_args)
                # # Store mapping of prompt to image data
                # image_prompt = tool_args.get("prompt", "generated_image")
                # state["knowledge"]["generated_images"][image_prompt] = result
                result = "nothing is generated yet"

            logging.info(f"UI Tool '{tool_name}' executed with args: {tool_args}")

            # Create tool message
            tool_outputs.append(
                ToolMessage(
                    content=str(result),
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            **state,
            "ui_messages": state["ui_messages"] + tool_outputs,
        }

    return state


# Research Agent - consolidates RAG, web search, and image search
def research_agent_node(state: AgentState) -> Dict[str, Any]:
    """Research agent that uses tools to gather knowledge and updates state."""
    logging.info("Research agent processing request")

    # Initialize knowledge if not present
    if "knowledge" not in state:
        state["knowledge"] = {
            "docs": [],
            "search": [],
            "images": [],
            "ui_images": [],
            "generated_images": {},
        }

    # Initialize iteration count if not present
    if "iteration_count" not in state:
        state["iteration_count"] = 0

    # Increment iteration count
    state["iteration_count"] += 1

    # Stop after 3 iterations to prevent infinite loops
    if state["iteration_count"] > 3:
        logging.info("Max iterations reached, proceeding to UI generation")
        return {**state}

    # Call LLM with tools - it will decide which tools to use
    response = research_llm_with_tools.invoke(state["messages"])

    # Update messages with the LLM response
    updated_messages = state["messages"] + [response]

    return {**state, "messages": updated_messages}


# UI condition checker for tool routing
def ui_tools_condition(state: AgentState):
    """Check if UI tools should be called."""
    if "ui_messages" not in state or not state["ui_messages"]:
        return END

    last_message = state["ui_messages"][-1]

    # Check if the last message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "ui_tools"
    else:
        return END


# UI Designer Agent - Creates a creative design plan with tool support
async def ui_designer_node(state: AgentState):
    """UI Designer creates a comprehensive design plan with visual assets."""
    logging.info("UI Designer creating design plan")

    prompt = state["prompt"]
    docs = state["knowledge"]["docs"]
    search_results = state["knowledge"]["search"]
    image_results = state["knowledge"]["images"]

    # Initialize UI messages if not present
    if "ui_messages" not in state:
        state["ui_messages"] = []

    # Prepare context for design planning
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

    # Prepare RAG context summary
    rag_summary = ""
    if docs:
        rag_summary = f"\nEDUCATIONAL MATERIALS AVAILABLE ({len(docs)} excerpts):\n"
        for i, doc in enumerate(docs[:3]):
            filename = doc.metadata.get("filename", "Unknown")
            preview = (
                doc.page_content[:150] + "..."
                if len(doc.page_content) > 150
                else doc.page_content
            )
            rag_summary += f"- {filename}: {preview}\n"

    # Add creativity elements
    themes = [
        "modern",
        "minimalist",
        "vibrant",
        "professional",
        "creative",
        "elegant",
        "playful",
        "dark",
        "light",
        "colorful",
    ]
    selected_theme = random.choice(themes)
    layout_seed = random.randint(1, 100)

    design_prompt = f"""You are a world-class UI/UX Designer creating innovative, beautiful user experiences. Your job is to create a comprehensive DESIGN PLAN (not final components yet).

AVAILABLE TOOLS FOR VISUAL ENHANCEMENT:
1. ui_image_search_tool_fn - Search for UI inspiration images
2. imagen_generate_tool_fn - Generate custom images (limit 1 per request)

USER REQUEST: "{prompt}"
DESIGN THEME: {selected_theme}
CREATIVE SEED: {layout_seed}

RESEARCH CONTEXT:
{search_context if search_context else "No search results - use your knowledge"}

AVAILABLE IMAGES:
{image_context if image_context else "No images available"}

{rag_summary}

YOUR MISSION:
1. FIRST: Decide if you need visual assets:
   - Use ui_image_search_tool_fn for UI inspiration if helpful
   - Use imagen_generate_tool_fn if a custom hero image would enhance the design (MAX 1 image)

2. THEN: Create a detailed DESIGN PLAN covering:
   - Overall visual concept and {selected_theme} theme application
   - Component selection strategy (3-5 different types for variety)
   - Content hierarchy and user flow
   - Visual elements and color psychology
   - How to integrate any research findings creatively
   - Specific content recommendations for each component type

COMPONENT TYPES AVAILABLE:
- **hero**: Featured banner with image, title, subtitle, CTA
- **card**: Content blocks with images, badges, descriptions  
- **gallery**: Image collections with captions
- **list**: Organized items with icons and descriptions
- **stats**: Data displays with metrics and icons
- **testimonial**: Quotes with author info and avatars

DESIGN PRINCIPLES:
- Maximize visual diversity and engagement
- Create emotional connection with users
- Ensure accessibility and readability
- Balance informational and visual components
- Apply {selected_theme} theme consistently
- Use the creative seed {layout_seed} for unique layout decisions

If you use tools, execute them first, then create your comprehensive design plan.
Output your design plan as clear, detailed text (not JSON).
"""

    # Call UI LLM with tools - it will decide which tools to use first
    response = ui_llm_with_tools.invoke([HumanMessage(content=design_prompt)])

    # Update UI messages with the LLM response
    ui_messages = state["ui_messages"] + [HumanMessage(content=design_prompt), response]

    return {**state, "ui_messages": ui_messages}


# Extract design plan from UI messages
def extract_design_plan_node(state: AgentState) -> Dict[str, Any]:
    """Extract the design plan from UI Designer's response."""
    logging.info("Extracting design plan from UI Designer")

    if "ui_messages" in state and state["ui_messages"]:
        # Get the last AI message which should contain the design plan
        for message in reversed(state["ui_messages"]):
            if hasattr(message, "content") and message.content:
                # Store the design plan in state
                return {**state, "design_plan": message.content}

    # Fallback if no design plan found
    return {**state, "design_plan": "No design plan available"}


async def ui_implementer_node(state: AgentState):
    """UI Implementer converts the design plan to final JSON components."""
    logging.info("UI Implementer creating final components")

    prompt = state["prompt"]
    design_plan = state.get("design_plan", "")
    ui_images = state["knowledge"]["ui_images"]
    generated_images = state["knowledge"]["generated_images"]
    docs = state["knowledge"]["docs"]
    search_results = state["knowledge"]["search"]
    image_results = state["knowledge"]["images"]

    # Helper function to map image prompts back to actual image data
    def resolve_image_reference(image_ref: str) -> str:
        """Resolve image reference to actual image data or URL."""
        # Check if it's a generated image prompt
        if image_ref in generated_images:
            return generated_images[image_ref]
        # Otherwise return as-is (could be a URL from search results)
        return image_ref

    # Prepare context summaries for reference
    search_summary = ""
    if search_results:
        search_summary = f"Search Results Summary: {len(search_results)} results available including topics like: "
        topics = [result.get("title", "")[:50] for result in search_results[:3]]
        search_summary += ", ".join(topics)

    image_summary = ""
    if image_results:
        image_summary = f"Images Available: {len(image_results)} images found"

    ui_image_context = ""
    if ui_images:
        for i, img in enumerate(ui_images[:4]):
            ui_image_context += f"UI Inspiration {i + 1}: {img.get('title', '')} - {img.get('image', '')}\n"

    generated_image_context = ""
    if generated_images:
        available_prompts = list(generated_images.keys())
        for i, prompt in enumerate(available_prompts):
            generated_image_context += (
                f"Generated Image {i + 1}: '{prompt}' (reference as: {prompt})\n"
            )

    rag_summary = ""
    if docs:
        rag_summary = f"Educational Materials: {len(docs)} excerpts available"

    implementation_prompt = f"""You are a UI Implementation Specialist. Your job is to convert the design plan into exact JSON components.

ORIGINAL USER REQUEST: "{prompt}"

DESIGN PLAN TO IMPLEMENT:
{design_plan}

AVAILABLE ASSETS:
{search_summary}
{image_summary}
{rag_summary}

UI INSPIRATION IMAGES:
{ui_image_context if ui_image_context else "No UI inspiration images"}

GENERATED IMAGES (reference by prompt in image fields):
{generated_image_context if generated_image_context else "No generated images"}

IMPLEMENTATION REQUIREMENTS:
1. Follow the design plan exactly as specified
2. Create 3-5 components using DIFFERENT types for variety
3. For generated images, use the exact prompt text as the image value (e.g., "A modern tech hero image")
4. Make titles concise (max 60 chars) and content readable (max 200 chars for cards)
5. Ensure visual diversity and engagement

Return ONLY a valid JSON object (no markdown, no explanations):
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
hero: {{"title": "string", "subtitle": "string", "image": "url_or_generated_prompt", "buttonText": "string", "buttonLink": "url_or_empty"}}
card: {{"title": "string", "content": "string", "image": "url_or_generated_prompt", "badge": "string_or_empty"}}
gallery: {{"title": "string", "images": [{{"url": "url_or_generated_prompt", "caption": "string"}}]}}
list: {{"title": "string", "items": [{{"text": "string", "icon": "emoji"}}]}}
stats: {{"title": "string", "data": [{{"value": "string", "label": "string", "icon": "emoji"}}]}}
testimonial: {{"quote": "string", "author": "string", "role": "string", "avatar": "url_or_generated_prompt"}}
"""

    try:
        response = ui_llm.invoke([HumanMessage(content=implementation_prompt)])
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        ui_components = json.loads(content)

        # Post-process components to resolve image references
        def resolve_component_images(component):
            """Recursively resolve image references in a component."""
            if isinstance(component, dict):
                for key, value in component.items():
                    if key == "image" and isinstance(value, str):
                        component[key] = resolve_image_reference(value)
                    elif key == "images" and isinstance(value, list):
                        for img_item in value:
                            if isinstance(img_item, dict) and "url" in img_item:
                                img_item["url"] = resolve_image_reference(
                                    img_item["url"]
                                )
                    elif key == "avatar" and isinstance(value, str):
                        component[key] = resolve_image_reference(value)
                    elif isinstance(value, (dict, list)):
                        resolve_component_images(value)
            elif isinstance(component, list):
                for item in component:
                    resolve_component_images(item)

        # Resolve all image references in the components
        resolve_component_images(ui_components)

        return {
            **state,
            "final_ui": ui_components,
            "messages": state["messages"]
            + [
                AIMessage(
                    content="UI components implemented successfully from design plan"
                )
            ],
        }

    except Exception as e:
        logging.error(f"UI Implementer error: {e}")
        # Fallback UI
        fallback_ui = {
            "components": [
                {
                    "type": "card",
                    "props": {
                        "title": "Design Implementation",
                        "content": "UI generated based on creative design plan with AI-powered enhancements.",
                        "badge": "AI Designed",
                    },
                }
            ]
        }
        return {
            **state,
            "final_ui": fallback_ui,
            "messages": state["messages"]
            + [
                AIMessage(content=f"UI implementation failed, using fallback: {str(e)}")
            ],
        }


# Create the graph-based workflow
def create_graph_workflow():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_agent_node)
    workflow.add_node("tools", custom_tool_node)
    workflow.add_node("ui_designer", ui_designer_node)
    workflow.add_node("ui_tools", ui_tool_node)
    workflow.add_node("extract_design", extract_design_plan_node)
    workflow.add_node("ui_implementer", ui_implementer_node)

    # Entry starts with research
    workflow.set_entry_point("research")

    # Add conditional edges from research
    workflow.add_conditional_edges(
        "research",
        tools_condition,
        {
            "tools": "tools",
            END: "ui_designer",
        },
    )

    # After research tool use, go back to research
    workflow.add_edge("tools", "research")

    # Add conditional edges from UI designer
    workflow.add_conditional_edges(
        "ui_designer",
        ui_tools_condition,
        {
            "ui_tools": "ui_tools",
            END: "extract_design",
        },
    )

    # After UI tool use, extract design plan
    workflow.add_edge("ui_tools", "extract_design")

    # After extracting design plan, implement UI
    workflow.add_edge("extract_design", "ui_implementer")

    # End after UI implementation
    workflow.add_edge("ui_implementer", END)

    return workflow.compile()


# Create the compiled workflow
graph_workflow = create_graph_workflow()

# NOTE: this somehow is not local it uses the mermaid api to render the graph
# graph_workflow.get_graph().draw_mermaid_png(output_file_path="graph_workflow.png")


async def process_prompt(prompt: str, user_id: str = "anonymous") -> Dict[str, Any]:
    """Main function to process a prompt using the graph-based workflow"""
    logging.info(f"Processing prompt with enhanced graph workflow: {prompt}")

    try:
        # Initialize the state
        initial_state = {
            "messages": [
                HumanMessage(
                    content="You are a helpful research agent who will gather content related to the user's query using available tools. The information will be used by a UI generator to create beautiful interfaces. Gather comprehensive information and stop when you have enough for quality UI generation."
                ),
                HumanMessage(content=f"User prompt: {prompt}"),
            ],
            "ui_messages": [],
            "prompt": prompt,
            "knowledge": {
                "docs": [],
                "search": [],
                "images": [],
                "ui_images": [],
                "generated_images": {},
            },
            "design_plan": "",
            "final_ui": {},
            "user_id": user_id,
            "iteration_count": 0,
        }

        # Run the workflow with recursion limit
        result = await graph_workflow.ainvoke(initial_state, {"recursion_limit": 10})

        logging.info("Enhanced graph workflow completed successfully")
        return result["final_ui"]

    except Exception as e:
        logging.exception("Error in enhanced graph workflow:")
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
