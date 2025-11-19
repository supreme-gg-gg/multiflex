import os
import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_prompt
from upload import router as upload_router
from html_agent_react import process_html_request, process_followup_request
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MultiFlex API")

# Add CORS middleware
# Configure CORS for both development and production
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str
    user_id: str = "anonymous"


class ChatMessage(BaseModel):
    message: str
    session_id: str = None
    user_id: str = "anonymous"


# Include upload router
app.include_router(upload_router, prefix="/api", tags=["upload"])


@app.get("/")
async def root():
    return {"message": "MultiFlex API is running"}


@app.post("/api/agent")
async def agent_endpoint(request: PromptRequest):
    try:
        result = await process_prompt(request.prompt, request.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("🔌 WebSocket connection attempt")
    await websocket.accept()
    logger.info("✅ WebSocket connection accepted")

    session_id = None
    current_html = ""

    try:
        # Receive the initial prompt
        logger.info("📥 Waiting for initial prompt...")
        initial_data = await websocket.receive_json()
        prompt = initial_data.get("prompt")
        user_id = initial_data.get("user_id", "anonymous")
        logger.info(f"📋 Received initial prompt: {prompt}")

        if not prompt:
            logger.warning("❌ No prompt provided, closing connection")
            await websocket.close(code=1008, reason="Prompt is required")
            return

        # Generate and send the initial HTML using new agent
        logger.info("🎨 Generating initial HTML with integrated agent...")
        result = await process_html_request(prompt, user_id)

        if result["success"]:
            current_html = result["html_content"]
            session_id = result["session_id"]

            # Send initial response
            response = {
                "type": "html_update",
                "html_content": current_html,
                "session_id": session_id,
            }
            await websocket.send_text(json.dumps(response))
            logger.info(f"✅ Initial HTML sent successfully (session: {session_id})")
        else:
            # Send error response
            error_response = {
                "type": "error",
                "message": result.get("error", "Failed to generate HTML"),
            }
            await websocket.send_text(json.dumps(error_response))
            return

        # Listen for follow-up messages and interactions
        logger.info("👂 Listening for follow-up messages...")
        while True:
            try:
                logger.info("⏳ Waiting for message...")
                message_data = await websocket.receive_json()
                logger.info(f"📨 Received message: {message_data}")

                message_type = message_data.get("type", "unknown")

                if message_type == "chat_message":
                    # Handle follow-up chat message
                    followup_message = message_data.get("message")
                    if followup_message and session_id:
                        logger.info(f"💬 Processing follow-up: {followup_message}")

                        # Process follow-up request
                        result = await process_followup_request(
                            followup_message, session_id, current_html, user_id
                        )

                        if result["success"]:
                            current_html = result["html_content"]
                            response = {
                                "type": "html_update",
                                "html_content": current_html,
                                "session_id": session_id,
                            }
                        else:
                            response = {
                                "type": "error",
                                "message": result.get(
                                    "error", "Failed to process follow-up"
                                ),
                            }

                        await websocket.send_text(json.dumps(response))
                        logger.info("✅ Follow-up response sent")

                elif message_type == "interaction":
                    # Handle UI interactions (legacy support)
                    logger.info("🎯 Received UI interaction (legacy mode)")
                    # For now, treat interactions as chat messages
                    action = message_data.get("action", "click")
                    element_id = message_data.get("element_id", "unknown")
                    interaction_text = f"User {action} on element {element_id}"

                    if session_id:
                        result = await process_followup_request(
                            interaction_text, session_id, current_html, user_id
                        )

                        if result["success"]:
                            current_html = result["html_content"]
                            response = {
                                "type": "html_update",
                                "html_content": current_html,
                                "session_id": session_id,
                            }
                            await websocket.send_text(json.dumps(response))
                            logger.info("✅ Interaction response sent")

            except WebSocketDisconnect:
                logger.info("🔌 WebSocket client disconnected")
                break
            except Exception as message_error:
                logger.error(f"❌ Message processing error: {message_error}")
                error_response = {"type": "error", "message": str(message_error)}
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected during initial setup")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        logger.info("🔌 Closing WebSocket connection")
        if session_id:
            logger.info(f"Session {session_id} ended")
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
