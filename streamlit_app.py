"""IBM Solution Finder - Main Streamlit Application.

This is the main entry point for the IBM Solution Finder application.
It configures the Streamlit multi-page app, sets up navigation, provides
sidebar controls for LLM configuration, and manages knowledge base synchronization.
"""

from typing import Any, Callable
import textwrap
import platform
import streamlit as st
import utils.ollama_utils as ollama_utils
from utils.logging_config import setup_logging
from config.settings import Settings as Config
from config.prompts import DEFAULT_SYSTEM_PROMPT
from config.urls import SEED_URLS

# Setup logging
logger = setup_logging()
logger.info(f"Starting IBM Solution Finder v{Config.APP_VERSION}")

# Define application pages
page_1: st.Page = st.Page(
    "views/solution_finder.py",
    title="Solution Finder",
    icon="🚀",
    default=True
)

page_2: st.Page = st.Page(
    "views/database_viewer.py",
    title="Knowledge Base",
    icon="🔍"
)

# Create multi-page navigation structure
pg: st.navigation = st.navigation({
    "Main Engine": [page_1],
    "System Tools": [page_2]
})


# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("Engine Configuration")

    # Retrieve available Ollama models
    available_models: list[str] = ollama_utils.get_available_models()

    # Model selection dropdown
    st.selectbox(
        "LLM Model",
        available_models,
        index=0,
        help="Select the local AI model you want to run.",
        key="selected_model"
    )

    # Collapsible system instructions section
    with st.expander("System Instructions", expanded=False):
        st.text_area(
            "LLM Instructions",
            value=DEFAULT_SYSTEM_PROMPT,
            height=450,
            key="system_prompt"
        )

    st.divider()

    st.header("Knowledge Management")
    
    # Knowledge synchronization button
    if st.button("Sync Knowledge", use_container_width=True):
        # Create UI placeholders for progress tracking
        progress_bar: Any = st.progress(0)
        status_text: Any = st.empty()
        stats_placeholder: Any = st.empty()
        
        def update_progress(stats: dict[str, int]) -> None:
            """Update progress bar and status text during crawling.
            
            Args:
                stats: Dictionary containing crawl statistics with keys:
                    - discovered: Total URLs discovered
                    - processed: Number of pages processed
                    - pending: Number of pages pending processing
            """
            total: int = stats.get('discovered', 0)
            processed: int = stats.get('processed', 0)
            
            if total > 0:
                progress: float = processed / total
                progress_bar.progress(min(progress, 1.0))
            
            status_text.text(
                f"Crawling: {processed} pages processed, "
                f"{stats.get('pending', 0)} pending..."
            )
        
        try:
            # Execute knowledge ingestion with progress callback
            stats: dict[str, int] = ollama_utils.ingest_knowledge(
                SEED_URLS,
                progress_callback=update_progress
            )
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display success message
            st.success("✅ Knowledge sync complete!")
            
            # Show final crawl statistics
            stats_placeholder.markdown(f"""
            **Crawl Statistics:**
            - Pages crawled: {stats.get('pages', 0)}
            - Chunks created: {stats.get('chunks', 0)}
            - URLs discovered: {stats.get('discovered', 0)}
            - Failed pages: {stats.get('failed', 0)}
            """)
            
        except Exception as e:
            # Clear progress indicators on error
            progress_bar.empty()
            status_text.empty()
            st.error(f"Error during sync: {str(e)}")
            st.exception(e)

    st.divider()

    # Display Python environment version
    st.caption(f"Environment: Python {platform.python_version()}")

pg.run()