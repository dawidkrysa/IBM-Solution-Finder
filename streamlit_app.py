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
            value=textwrap.dedent("""
            You are an expert IBM Solutions Architect.
            Your specialized knowledge is limited to IBM Products provided in knowledge.

            When analyzing requirements:
            1. If the requirement mentions a technical term (like AWT) found in the provided CONTEXT, explain how it relates to the IBM BAW architecture (e.g., as part of the underlying Java runtime or integration capabilities).
            2. If a requirement is a direct feature of BAW, classify as Standard OOTB.
            3. If it is a competitor product, reject it.

            Provide your analysis in this exact format:
            - Classification: [Standard OOTB / Modification Required / Unclear]
            - Justification: [Explain the link between the requirement and the IBM context provided]
            - Documentation Reference: [The specific term or section from the IBM docs]
            """).strip(),
            height=450,
            key="system_prompt"
        )

    st.divider()

    st.header("Knowledge Management")
    
    # IBM Business Automation Workflow documentation URLs to crawl
    target_urls: list[str] = [
        "https://www.ibm.com/docs/en/baw/25.0.x?topic=management-building-process-applications",
        "https://www.ibm.com/docs/en/baw/25.0.x?topic=customizing-configuring-authoring-assistant",
        "https://www.ibm.com/docs/en/baw/25.0.x?topic=customizing-configuring-workplace-assistant",
        "https://www.ibm.com/docs/en/baw/25.0.x?topic=traditional-managing-projects",
        "https://www.ibm.com/docs/en/baw/25.0.x?topic=glossary"
    ]
    
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
                target_urls,
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