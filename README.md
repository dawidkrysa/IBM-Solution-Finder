# IBM Solution Finder

A Retrieval-Augmented Generation (RAG) application that analyzes project requirements against IBM Business Automation Workflow (BAW) documentation to determine solution feasibility and classification.

## Overview

This application combines local LLM inference (via Ollama) with vector-based knowledge retrieval to provide intelligent analysis of project requirements. It crawls IBM BAW documentation, stores it in a vector database, and uses semantic search to augment LLM responses with relevant context.

## Features

- **Local LLM Integration**: Connects to Ollama for private, on-premise AI inference
- **RAG Architecture**: Retrieves relevant IBM documentation context before generating responses
- **Knowledge Synchronization**: Crawls and indexes IBM BAW documentation automatically
- **Interactive UI**: Streamlit-based dashboard for easy requirement analysis
- **Configurable System Prompts**: Customize LLM behavior for specific use cases
- **Docker Deployment**: Fully containerized with GPU support

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│  (Port 8501)    │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────┐
│  Ollama Engine  │  │  ChromaDB    │
│  (Port 11434)   │  │  (Vector DB) │
└─────────────────┘  └──────────────┘
```

## Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with CUDA support (for optimal performance)
- NVIDIA Container Toolkit
- At least 8GB RAM
- 10GB free disk space

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OOTB-Analysis
   ```

2. **Configure Ollama model storage** (optional)
   
   Edit `docker-compose.yml` to set your preferred model storage location:
   ```yaml
   volumes:
     - D:/OllamaModels:/root/.ollama  # Change this path
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Download an Ollama model**
   ```bash
   docker exec -it ollama-engine ollama pull llama3.2
   ```

5. **Access the application**
   
   Open your browser to: `http://localhost:8501`

## Usage

### 1. Sync Knowledge Base

Click the **"Sync Knowledge"** button in the sidebar to crawl and index IBM BAW documentation.

**Selenium Crawler Features:**
- **JavaScript Execution**: Uses Chrome to render JavaScript-heavy pages
- **Smart URL Handling**: Properly handles IBM's query parameter structure (`?topic=...`)
- **Breadth-First Crawling**: Systematically explores documentation up to depth 2
- **Duplicate Prevention**: Advanced URL normalization and tracking
- **Progress Tracking**: Real-time updates on crawling progress
- **Content Validation**: Ensures quality documentation content
- **Rate Limiting**: 2-second delay between requests (Selenium is slower)

**What happens during sync:**
1. Initializes Chrome browser in headless mode
2. Crawls from 5 seed URLs up to 2 levels deep
3. Waits for JavaScript to render on each page
4. Extracts clean content after page load
5. Validates and normalizes all discovered URLs
6. Splits content into 1000-character chunks with 100-char overlap
7. Generates embeddings using `all-MiniLM-L6-v2`
8. Stores vectors in ChromaDB
9. Shows detailed statistics (pages crawled, chunks created, failures)

**Expected Results:**
- Pages crawled: 50-100 (depending on depth and limits)
- Chunks created: 500-2,000
- Crawl time: 5-15 minutes (slower but gets real content)

### 2. Select Model

Choose your preferred Ollama model from the dropdown. Available models depend on what you've downloaded.

### 3. Configure System Prompt (Optional)

Expand the "System Prompt Configuration" section to customize the LLM's behavior and analysis criteria.

### 4. Analyze Requirements

1. Paste your project requirements in the text area
2. Click **"Analyze Requirements"**
3. The system will:
   - Retrieve relevant IBM documentation context
   - Augment your prompt with this context
   - Generate a classification and justification

## Configuration

### Crawler Settings

The Selenium crawler can be configured in `utils/ollama_utils.py`:

```python
crawler = SeleniumIBMCrawler(
    max_depth=2,           # Crawl depth (1-3 recommended)
    max_pages=100,         # Maximum pages to crawl
    delay=2.0,             # Seconds between requests
    page_load_timeout=30   # Page load timeout in seconds
)
```

**Performance Tips:**
- Lower `max_depth` for faster crawls (1 = seed URLs only)
- Lower `max_pages` to limit total pages
- Increase `delay` if getting blocked
- Selenium uses more resources than simple HTTP requests

### Target Documentation URLs

The application starts crawling from these seed URLs:

```python
target_urls = [
    "https://www.ibm.com/docs/en/baw/25.0.x?topic=management-building-process-applications",
    "https://www.ibm.com/docs/en/baw/25.0.x?topic=customizing-configuring-authoring-assistant",
    "https://www.ibm.com/docs/en/baw/25.0.x?topic=customizing-configuring-workplace-assistant",
    "https://www.ibm.com/docs/en/baw/25.0.x?topic=traditional-managing-projects",
    "https://www.ibm.com/docs/en/baw/25.0.x?topic=glossary"
]
```

Modify these in [`streamlit_app.py`](streamlit_app.py:69-75) to start from different documentation sections.

### System Prompt

The default system prompt configures the LLM as an IBM Solutions Architect specializing in BAW. It provides classification criteria:

- **Standard OOTB**: Direct BAW feature
- **Modification Required**: Requires customization
- **Unclear**: Insufficient information

### Vector Database

- **Storage**: `/app/chroma_db` (persisted via Docker volume)
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Chunk Size**: 1000 characters with 100-character overlap
- **Retrieval**: Top 3 most relevant chunks per query

## Project Structure

```
.
├── streamlit_app.py              # Main Streamlit application
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Streamlit container with Chrome
├── docker-compose.yml            # Multi-container orchestration
├── README.md                     # This file
├── .dockerignore                 # Files to exclude from Docker build
├── utils/
│   ├── ollama_utils.py          # Ollama API & RAG orchestration
│   ├── selenium_crawler.py      # Selenium-based crawler for JavaScript sites
│   └── url_utils.py             # URL normalization and validation
├── views/
│   ├── solution_finder.py       # Main analysis interface
│   └── database_viewer.py       # Knowledge base inspector
├── .devcontainer/               # VS Code dev container config
└── chroma_db/                   # Vector database storage (created at runtime)
```

## Dependencies

### Python Packages

- **streamlit**: Web UI framework
- **langchain**: LLM orchestration framework
- **langchain-community**: Community integrations
- **langchain-chroma**: ChromaDB vector store
- **langchain-huggingface**: HuggingFace embeddings
- **chromadb**: Vector database
- **sentence-transformers**: Embedding models
- **beautifulsoup4**: HTML parsing
- **requests**: HTTP client

### Docker Services

- **streamlit-app**: Python 3.11 slim with Streamlit
- **ollama-engine**: Ollama LLM inference engine

## API Endpoints

### Ollama Engine

- **List Models**: `GET http://ollama-engine:11434/api/tags`
- **Generate Response**: `POST http://ollama-engine:11434/api/generate`

## Troubleshooting

### No models available

```bash
# Pull a model manually
docker exec -it ollama-engine ollama pull llama3.2
```

### Connection refused to Ollama

```bash
# Check if Ollama container is running
docker ps | grep ollama-engine

# Restart services
docker-compose restart
```

### Knowledge sync fails

**Symptoms:** Sync button shows error or very few pages crawled

**Solutions:**
- Ensure internet connectivity
- Check IBM documentation URLs are accessible in browser
- Verify sufficient disk space for vector database
- Check Docker logs: `docker-compose logs -f streamlit-app`
- Try reducing `max_depth` or `max_pages` in configuration
- Verify the seed URLs are still valid (IBM may change documentation structure)

### Crawl takes too long

**Symptoms:** Sync runs for more than 30 minutes

**Solutions:**
- Reduce `max_pages` limit (default: 500)
- Reduce `max_depth` (default: 3)
- Check if crawler is stuck on specific URLs in logs

### GPU not detected

```bash
# Verify NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## Performance Optimization

- **GPU Acceleration**: Enabled by default for Ollama
- **Model Selection**: Smaller models (7B parameters) for faster inference
- **Chunk Size**: Adjust in [`ollama_utils.py`](ollama_utils.py:62) for different document types
- **Retrieval Count**: Modify `k=3` in [`get_context()`](ollama_utils.py:81) to retrieve more/fewer chunks

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit locally
streamlit run streamlit_app.py
```

### VS Code Dev Container

The project includes a `.devcontainer` configuration for containerized development.

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues related to:
- **IBM BAW Documentation**: Contact IBM Support
- **Ollama**: Visit [ollama.ai](https://ollama.ai)
- **This Application**: [Add your contact/issue tracker]

## Acknowledgments

- IBM Business Automation Workflow documentation
- Ollama for local LLM inference
- LangChain for RAG orchestration
- ChromaDB for vector storage