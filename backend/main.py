import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_prompt
from upload import router as upload_router

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
