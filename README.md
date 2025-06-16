# NUS Hacks 2025 Documentation

A sophisticated prototype featuring a dynamic, responsive UI that generates interfaces on-demand using a backend agent built with Google Agent Development Kit (ADK) and a React frontend.

## 🏗️ Architecture

```plaintext
Frontend (Next.js/TypeScript)     Agent Backend (Python)         Google Cloud
┌─────────────────────┐          ┌──────────────────┐          ┌─────────────┐
│                     │          │                  │          │             │
│  • React Components │   HTTP   │  • LangGraph     │          │  Firestore  │
│  • Dynamic Canvas   │ ◄──────► │  • Tools/LLM     │ ◄──────► │  Database   │
│  • UI Renderers     │          │  • FastAPI       │          │             │
│                     │          │                  │          └─────────────┘
└─────────────────────┘          └──────────────────┘                │
                                           │                         │
                                           ▼                         │
                                    ┌──────────────────┐             │
                                    │  Google Cloud    │ ◄───────────┘
                                    │  Run Deployment  │
                                    └──────────────────┘
```

## 🚀 Features

### Backend (Python + ADK)

- **Agent Framework**: Built with Google Agent Development Kit
- **Dynamic Tool**: `process_user_request` - processes queries and generates UI specifications
- **LLM Integration**: Google Gemini 1.5 Pro for intelligent UI generation
- **User Profiles**: Firestore-based user cognitive profiles and preferences
- **RESTful API**: FastAPI endpoints for frontend communication

### Frontend (Next.js + TypeScript)

- **Dynamic UI Rendering**: Real-time UI generation based on backend responses
- **Component Library**: 5 specialized UI renderers
  - **MarkdownRenderer**: Rich text and documentation
  - **TableGrid**: Interactive sortable/filterable data tables
  - **CardList**: Card-based data display with actions
  - **ChartView**: Data visualization with charts and graphs
  - **KeyValueList**: Simple key-value pair displays
- **Modern UI**: shadcn/ui components with Tailwind CSS
- **Responsive Design**: Mobile-first approach

### Cloud Infrastructure

- **Deployment**: Google Cloud Run for serverless scaling
- **Database**: Firestore for user profiles and interaction history
- **CI/CD**: Google Cloud Build for automated deployments

## 📁 Project Structure

```plaintext
nus-hacks/
├── frontend/                    # Next.js TypeScript application
│   ├── src/
│   │   ├── app/                # Next.js app directory
│   │   ├── components/         # Dynamic UI components
│   └── package.json
│
├── backend/                     # Python LangChain agent
│   ├── src/
│   │   ├── agent.py           # Main agent definition
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── README.md                   # Project documentation
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Cloud account with:
  - Cloud Run API enabled
  - Firestore database created
  - Service account with appropriate permissions
- Gemini API key

### Backend Setup

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run locally**:
   ```bash
   python -m src.main
   ```

### Frontend Setup

1. **Navigate to frontend directory**:

```bash
   cd frontend
```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```
