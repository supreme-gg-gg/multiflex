# Simplified Intelligent UI Generation System

This streamlined backend system uses LangGraph to create intelligent user interfaces with smart decision-making about when to search for content and images.

## 🧠 Intelligent Decision Making

The system includes a **Decision Agent** that analyzes each prompt and intelligently determines:

- **When to search**: For current events, detailed information, recent developments, complex topics
- **When to skip search**: For simple factual questions, basic definitions, general knowledge the LLM already knows
- **When to get images**: For visual content, galleries, products, places, things that benefit from visual representation
- **When to skip images**: For text-heavy content, lists, pure information, abstract concepts

## 🔄 Simple Workflow

```
User Prompt → Decision Agent → [Search Agent] → [Image Agent] → UI Generator → Final UI
```

**Smart Routing Examples:**

- _"What are two countries in North America?"_ → Skip search (simple knowledge), Get images (visual aid)
- _"Write a blog about climate change"_ → Search needed (current data), Skip images (text content)
- _"Show me modern architecture"_ → Search + Images (visual gallery with current examples)
- _"What is 2+2?"_ → Skip both (simple math, no visuals needed)

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Google API Key for Gemini

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment:

```bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

3. Run the server:

```bash
python src/main.py
```

API available at `http://localhost:8000`

## 🔧 API Usage

### POST /api/agent

**Request:**

```json
{
  "prompt": "artificial intelligence in healthcare"
}
```

**Response:**

```json
{
  "components": [
    {
      "type": "hero",
      "props": {
        "title": "AI in Healthcare",
        "subtitle": "Revolutionizing medical diagnosis and treatment",
        "image": "https://example.com/ai-healthcare.jpg",
        "buttonText": "Learn More",
        "buttonLink": "#learn-more"
      }
    },
    {
      "type": "card",
      "props": {
        "title": "Key Applications",
        "content": "AI is transforming diagnostics, drug discovery, and personalized treatment plans.",
        "badge": "Innovation"
      }
    }
  ]
}
```

## 🎯 Component Types

- **hero**: Large featured banners with call-to-action
- **card**: Information cards with optional images and badges
- **gallery**: Image collections with captions
- **list**: Organized content with icons and descriptions
- **stats**: Numerical data displays with icons
- **testimonial**: Quote displays with author information

## 🧪 Testing

Test the intelligent decision-making:

```bash
python test_simple_agent.py
```

This tests various scenarios:

- Simple questions (should skip search)
- Current events (should use search)
- Visual content (should get images)
- Text-heavy content (should skip images)

## ✨ Key Benefits

### Smart Resource Usage

- **Faster responses** for simple questions (no unnecessary searches)
- **Relevant content** when search is actually needed
- **Visual enhancement** only when appropriate
- **Cost efficient** by avoiding unnecessary API calls

### Simplified Architecture

- **4 focused agents** instead of complex multi-agent orchestration
- **Clear decision logic** that's easy to understand and modify
- **Robust error handling** with sensible fallbacks
- **Easy to extend** with additional decision criteria

## 📊 Decision Examples

| Prompt                           | Search Needed | Images Needed | Reasoning                                 |
| -------------------------------- | ------------- | ------------- | ----------------------------------------- |
| "What is Python?"                | ❌            | ❌            | Basic programming knowledge               |
| "Latest Python updates"          | ✅            | ❌            | Current events, text content              |
| "Beautiful Python code examples" | ✅            | ✅            | Examples + visual code snippets           |
| "Python vs Java performance"     | ✅            | ❌            | Needs current benchmarks, comparison data |
| "Show me Python logos"           | ❌            | ✅            | Simple request, visual content            |

## 🔄 Workflow Details

1. **Decision Agent**: Analyzes prompt and sets `needs_search` and `needs_images` flags
2. **Search Agent**: Conditionally searches for content if `needs_search = true`
3. **Image Agent**: Conditionally searches for images if `needs_images = true`
4. **UI Generator**: Creates components using available data (search results, images, or LLM knowledge)

## 🚀 Usage Examples

### Knowledge-based (no search needed)

```bash
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the primary colors?"}'
```

### Current events (search needed)

```bash
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Latest developments in renewable energy"}'
```

### Visual content (images needed)

```bash
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Modern minimalist interior design"}'
```

The system automatically determines the optimal approach for each request!

## 📈 Performance

- **Fast responses** for knowledge-based queries (no external calls)
- **Targeted searches** only when necessary
- **Efficient image retrieval** for visual content
- **Graceful degradation** when services are unavailable

## 🔧 Configuration

The decision logic can be customized by modifying the decision prompt in `decision_agent_node()`. Current criteria:

- **Search triggers**: current events, research, news, statistics, complex topics
- **Image triggers**: visual content, galleries, products, places, demonstrations
- **Skip conditions**: simple knowledge, basic math, definitions, abstract concepts

This intelligent system provides the perfect balance of functionality and simplicity!
