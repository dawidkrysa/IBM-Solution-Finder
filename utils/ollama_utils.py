"""Ollama Utilities Module.

This module provides utilities for interacting with Ollama AI models and managing
the ChromaDB vector database for document retrieval and knowledge ingestion.
It handles model listing, response generation, document crawling, and context retrieval.
"""

from typing import Any, Callable, Optional
import os
import logging
import chromadb
from config import Config
from utils.validation import sanitize_error_message

from requests import Response, get, post
from requests.exceptions import RequestException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from utils.selenium_crawler import SeleniumCrawler


# Configure logging
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

# ChromaDB persistence directory path
DB_PATH: str = Config.CHROMA_DB_PATH

# ChromaDB client settings - consistent across all operations
CHROMA_SETTINGS = chromadb.Settings(
    anonymized_telemetry=False,
    allow_reset=True
)


def get_available_models() -> list[str]:
    """Retrieve list of available Ollama models.
    
    Queries the Ollama API to get all downloaded models available for use.
    
    Returns:
        list[str]: List of model names. Returns placeholder message if no models
            are available or error message if connection fails.
    
    Examples:
        >>> models = get_available_models()
        >>> print(models)
        ['llama3', 'mistral', 'codellama']
    """
    try:
        # Query Ollama container via Docker network name
        response: Response = get(
            f"{Config.OLLAMA_BASE_URL}/api/tags",
            timeout=Config.OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        
        # Parse JSON response and extract model names
        models: list[dict[str, Any]] = response.json().get("models", [])
        model_names: list[str] = [model["name"] for model in models]
        
        # Return model names or placeholder if empty
        return model_names if model_names else ["No models downloaded yet"]
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return ["Error connecting to Ollama"]


def generate_response(
    selected_model: str,
    system_prompt: str,
    user_requirement: str,
    context: str
) -> str:
    """Generate AI response using Ollama with provided context.
    
    Sends a request to Ollama API with system prompt, user requirement, and
    retrieved context from documentation to generate a relevant response.
    
    Args:
        selected_model: Name of the Ollama model to use (e.g., 'llama3').
        system_prompt: System-level instructions for the AI model.
        user_requirement: User's project requirements or question.
        context: Retrieved documentation context from ChromaDB.
    
    Returns:
        str: Generated AI response or error message if request fails.
    
    Examples:
        >>> response = generate_response(
        ...     "llama3",
        ...     "You are an IBM expert",
        ...     "Need container orchestration",
        ...     "IBM Cloud Kubernetes Service..."
        ... )
        >>> print(response)
        'I recommend IBM Cloud Kubernetes Service...'
    """
    # Ollama API endpoint
    api_url: str = f"{Config.OLLAMA_BASE_URL}/api/generate"

    # Combine context and user requirement into full prompt
    full_prompt: str = (
        f"CONTEXT FROM IBM DOCUMENTATION:\n{context}\n\n"
        f"USER REQUIREMENT:\n{user_requirement}"
    )

    # Prepare request payload
    payload: dict[str, Any] = {
        "model": selected_model,
        "system": system_prompt,
        "prompt": full_prompt,
        "stream": False  # Request complete response at once
    }
    
    try:
        # Make API call to Ollama
        response: Response = post(api_url, json=payload)
        response.raise_for_status()
        
        # Extract AI response from JSON
        ai_response: str = response.json().get("response", "No response generated.")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        return f"Failed to connect to AI service. {sanitize_error_message(e)}"

def ingest_knowledge(
    urls: list[str],
    progress_callback: Optional[Callable[[dict[str, int]], None]] = None
) -> dict[str, int]:
    """Ingest IBM documentation into ChromaDB knowledge base.
    
    Crawls IBM documentation URLs using Selenium, splits content into chunks,
    generates embeddings, and stores in ChromaDB vector database for retrieval.
    
    Args:
        urls: List of seed URLs to start crawling from.
        progress_callback: Optional callback function for progress updates.
            Receives statistics dictionary with crawl progress information.
    
    Returns:
        dict[str, int]: Statistics dictionary containing:
            - chunks: Number of text chunks created
            - pages: Number of pages crawled
            - failed: Number of failed page loads
            - discovered: Number of URLs discovered
    
    Examples:
        >>> stats = ingest_knowledge(
        ...     ["https://www.ibm.com/docs/en/baw"],
        ...     progress_callback=lambda msg: print(msg)
        ... )
        >>> print(f"Ingested {stats['chunks']} chunks from {stats['pages']} pages")
    """
    logger.info(
        f"Starting knowledge ingestion from {len(urls)} seed URLs using Selenium"
    )
    
    # Initialize HuggingFace embeddings model
    embeddings: HuggingFaceEmbeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL
    )
    
    # Initialize Selenium web crawler with configuration
    crawler: SeleniumCrawler = SeleniumCrawler(
        max_depth=Config.CRAWLER_MAX_DEPTH,
        max_pages=Config.CRAWLER_MAX_PAGES,
        delay=Config.CRAWLER_DELAY,
        page_load_timeout=Config.CRAWLER_TIMEOUT
    )
    
    # Crawl URLs and collect raw documents
    logger.info("Starting Selenium crawl...")
    raw_documents: list[dict[str, Any]] = crawler.crawl(
        seed_urls=urls,
        progress_callback=progress_callback
    )
    
    logger.info(f"Crawled {len(raw_documents)} pages")
    
    # Handle case where no documents were crawled
    if not raw_documents:
        logger.warning("No documents were crawled!")
        return {
            "chunks": 0,
            "pages": 0,
            "failed": 0,
            "discovered": 0
        }
    
    # Convert raw documents to LangChain Document format
    langchain_docs: list[Document] = []
    for doc in raw_documents:
        langchain_docs.append(Document(
            page_content=doc['content'],
            metadata=doc['metadata']
        ))
    
    # Split documents into smaller chunks for better retrieval
    logger.info("Splitting documents into chunks...")
    text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    chunks: list[Document] = text_splitter.split_documents(langchain_docs)
    
    logger.info(f"Created {len(chunks)} chunks from {len(langchain_docs)} documents")
    
    # Store chunks in ChromaDB vector database
    logger.info("Storing in vector database...")
    vector_db: Chroma = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH,
        client_settings=CHROMA_SETTINGS
    )
    
    # Compile final statistics
    stats: dict[str, int] = crawler.get_stats()
    stats['chunks'] = len(chunks)
    stats['pages'] = len(langchain_docs)
    
    logger.info(f"Knowledge ingestion complete: {stats}")
    
    return stats


def get_context(query: str) -> list[Document]:
    """Retrieve relevant context documents from ChromaDB.
    
    Performs similarity search in the vector database to find the most relevant
    document chunks for the given query.
    
    Args:
        query: Search query string (user requirement or question).
    
    Returns:
        list[Document]: List of top 3 most relevant document chunks.
            Returns empty list if database doesn't exist.
    
    Examples:
        >>> docs = get_context("container orchestration")
        >>> for doc in docs:
        ...     print(doc.page_content[:100])
        'IBM Cloud Kubernetes Service provides...'
    """
    # Check if database exists
    if not os.path.exists(DB_PATH):
        return []
    
    # Initialize embeddings and database connection
    embeddings: HuggingFaceEmbeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL
    )
    db: Chroma = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
        client_settings=CHROMA_SETTINGS
    )
    
    # Retrieve top 3 most relevant document chunks
    docs: list[Document] = db.similarity_search(query, k=Config.RETRIEVAL_COUNT)

    return docs