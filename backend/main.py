import os
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_prompt
from upload import router as upload_router
from html_agent import generate_initial_html, process_interaction

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
    print("🔌 WebSocket connection attempt")
    await websocket.accept()
    print("✅ WebSocket connection accepted")

    html = ""
    try:
        # Receive the initial prompt
        print("📥 Waiting for initial prompt...")
        initial_data = await websocket.receive_json()
        prompt = initial_data.get("prompt")
        print(f"📋 Received initial prompt: {prompt}")

        if not prompt:
            print("❌ No prompt provided, closing connection")
            await websocket.close(code=1008, reason="Prompt is required")
            return

        # Generate and send the initial HTML
        print("🎨 Generating initial HTML...")
        html = generate_initial_html(prompt)
        print(f"📤 Sending initial HTML (length: {len(html)})")
        await websocket.send_text(html)
        print("✅ Initial HTML sent successfully")

        # Listen for user interactions
        print("👂 Listening for user iteractions...")
        while True:
            try:
                print("⏳ Waiting for interaction...")
                interaction = await websocket.receive_json()
                print(f"🎯 Received interaction: {interaction}")

                # Generate a full updated HTML page
                print("🔄 Processing interaction...")
                html = process_interaction(interaction, html)
                print(f"📤 Sending updated HTML (length: {len(html)})")
                await websocket.send_text(html)
                print("✅ Updated HTML sent successfully")

            except Exception as interaction_error:
                print(f"❌ Interaction error: {interaction_error}")
                break

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("🔌 Closing WebSocket connection")
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
