# MultiFlex

We want to challenge how search and information is traditionally presented in AI systems. That's why we built AI agents that **go beyond chat interface — our platform lets AI generate dynamic, visual interfaces tailored** to your question.

The vision was to build agents that replace traditional search, with a focus on investigating how agents can dynamically create user-interfaces for different purposes such as presenting information, running simulations, handling user interactions, etc by writing and updating code in real time. Instead of restricting agents to chat interfaces, we let them unleash their creativity and context-awareness. We weren't able to find good enough models at the time (that balances robustness and latency) and ran out of time at the hackathon, **but the same vision was later built by the team behind Google Search, [in their Gemini 3.0 release video](https://youtu.be/uYQGrK55gxQ?si=HcjwyVGd7VeifxYJ)**. DeepMind released a [research demo on Gemini 2.5 called "just-in-time generative UI"](https://developers.googleblog.com/en/simulating-a-neural-operating-system-with-gemini-2-5-flash-lite/) with the exact same vision as well one week after our hackathon.

> [!WARNING]
> **This project is no longer maintained!** This is a proof-of-concept prototype that may not work in production.

> View us on [Devpost (NUS Hacks)](https://devpost.com/software/multiflex?ref_content=my-projects-tab&ref_feature=my_projects) and our [demo video](https://youtu.be/Nu0qq5zvanM)

**Key Features:**

- Instead of just text, the AI can present answers as cards, tables, galleries, or custom layouts, choosing the best format for each context.
- With advanced multimodal capabilities, RAG, searches, and real-time image generation, the system delivers responses enriched with images, structured data, and interactive elements—making complex topics clearer and learning more engaging.

## Architecture

Our full stack multi-agent application leverages cloud technologies for scalability and performance and cutting edge AI models like Gemini and Imagen for advanced language and multimodal capabilities.

![Architecture](resources/design.png)

## Multi-Agent System

Our multi-agent architecture is orchestrated using LangGraph:

<p align="center">
   <img src="resources/graph_workflow.png" alt="Agents" width="40%">
</p>

### Research Agent

- **Purpose**: Gathers comprehensive information from multiple sources
- **Tools**: RAG search, web search, image search
- **LLM**: Gemini 2.0 Flash for research planning and synthesis
- **Output**: Consolidated knowledge base with documents, search results, and images

### UI Designer Agent

- **Purpose**: Creates interactive UI specifications based on research findings
- **Tools**: UI image search, Imagen generation for custom visuals
- **LLM**: Gemini 2.0 Flash (high creativity) for UI design
- **Output**: Dynamic UI components with embedded content and generated images

### LangGraph Orchestrator

- **Purpose**: Coordinates agent workflow and state management
- **Features**: Tool condition routing, state persistence, iteration control
- **Flow**: Research → UI Design → Response Generation

## Demo Photos

<p align="center">
   <img src="resources/home.png" alt="Demo 1" width="90%">
   <img src="resources/ui.png" alt="Demo 2" width="90%">
</p>

## Technology Stack

### Backend

- **Framework**: FastAPI with Uvicorn
- **AI/ML**: LangChain, LangGraph, Google Gemini 2.0 Flash
- **Vector Database**: ChromaDB with Google Embeddings
- **Search**: DuckDuckGo Search API
- **Image Generation**: Google Imagen
- **Document Processing**: Unstructured, PyPDF, python-docx

### Frontend

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Components**: Custom dynamic UI renderers
- **Build**: Static export for Firebase Hosting

### Infrastructure

- **Backend Hosting**: Google Cloud Run (serverless)
- **Frontend Hosting**: Firebase Hosting
- **CI/CD**: Google Cloud Build
- **Storage**: Google Cloud Storage (optional)

## For Developers

### Project Structure

```
nus-hacks/
├── backend/                     # Python FastAPI backend
│   ├── src/
│   │   ├── main.py             # FastAPI application
│   │   ├── agent.py            # LangGraph multi-agent workflow
│   │   ├── tools.py            # Research and UI generation tools
│   │   ├── rag_manager.py      # ChromaDB RAG implementation
│   │   └── upload.py           # Document upload handling
│   ├── vectorstore_data/       # ChromaDB persistence
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── .env.example           # Environment template
│
├── frontend/                   # Next.js TypeScript frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── page.tsx       # Main chat interface
│   │   │   ├── result/        # Response display page
│   │   │   ├── upload/        # Document upload page
│   │   │   └── manage/        # Document management
│   │   └── components/        # Dynamic UI components
│   │       ├── Card.tsx       # Content cards
│   │       ├── Gallery.tsx    # Image galleries
│   │       ├── Hero.tsx       # Hero sections
│   │       ├── List.tsx       # Interactive lists
│   │       ├── Stats.tsx      # Data displays
│   │       └── Testimonial.tsx # Quote blocks
│   ├── package.json           # Node.js dependencies
│   └── firebase.json          # Firebase configuration
│
├── cloudbuild.yaml            # Google Cloud Build configuration
└── README.md                  # This file
```

### Local Setup

#### Backend Setup

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

5. **Run the backend server**:

   ```bash
   # From the backend directory
   python -m src.main

   # Or using uvicorn directly (recommended)
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   Backend will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Configure environment** (create `.env.local`):

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run development server**:

   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3000`

#### API Testing

Test the backend directly:

```bash
curl -X POST "http://localhost:8000/api/agent" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum physics", "user_id": "test-user"}'
```
