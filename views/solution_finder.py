"""IBM Solution Finder View.

This module provides a Streamlit-based user interface for analyzing project
requirements and recommending IBM products based on documentation context.
It uses Ollama for AI-powered recommendations and ChromaDB for document retrieval.
"""

from typing import Any, Optional
import utils.ollama_utils as ollama_utils
import streamlit as st

# --- MAIN DASHBOARD ---
st.title("IBM Solution Finder")
st.markdown("Paste your project requirements below to see which IBM products can cover your needs.")


# Sample project requirements for quick testing
options: dict[str, str] = {
    "Sample: Approval Workflow": "Can we replace Pega with BAW for case management?",
    "Sample: Competitor Check": "We need to automate a multi-step approval process for HR.",
    "Custom": ""
}

# Handle sample selection and update session state
# When a user selects a sample, populate the text area with the corresponding requirement
if st.session_state.get("sample_selector"):
    selected_key: str = st.session_state.sample_selector
    
    # Update requirements text area input with selected sample
    st.session_state.req_input = options[selected_key]
    
    # Reset the state key so the widget draws as "unselected"
    st.session_state.sample_selector = None
    
    # Rerun to ensure the text area below sees the new req_input immediately
    st.rerun()

# Segmented control for quick sample selection
selection: Optional[str] = st.segmented_control(
    "Quick Select Samples:",
    options=list(options.keys()),
    selection_mode="single",
    key="sample_selector"
)

# User input text area for project requirements
user_input: str = st.text_area(
    "Project Requirements",
    height=150,
    placeholder="E.g., We need a secure, scalable container orchestration platform to run our microservices...",
    value=st.session_state.get("req_input", "")
)

# Main analysis button and processing logic
if st.button("Analyze Requirements", type="primary"):
    
    if not user_input.strip():
        st.warning("Please enter some project requirements first.")
    else:
        # Retrieve relevant context from ChromaDB vector store
        context_docs: list[Any] = ollama_utils.get_context(user_input)

        # Combine all document contents into a single context string
        context_text: str = "\n---\n".join([d.page_content for d in context_docs])

        # Create two-column layout: recommendations (2/3) and sources (1/3)
        res_col, src_col = st.columns([2, 1])

        with res_col:
            st.subheader("📋 Recommendation")
            with st.spinner("Consulting IBM Docs..."):
                # Retrieve model and prompt settings from session state
                selected_model: str = st.session_state.get("selected_model", "llama3")
                system_prompt: str = st.session_state.get("system_prompt", "")

                # Generate AI response using Ollama with retrieved context
                response: str = ollama_utils.generate_response(
                    selected_model,
                    system_prompt,
                    user_input,
                    context_text
                )
                st.markdown(response)

        with src_col:
            st.subheader("📚 Sources Used")
            # Display source documents used for context retrieval
            if context_docs:
                for i, doc in enumerate(context_docs):
                    with st.expander(f"Source {i+1}"):
                        st.caption(f"File/URL: {doc.metadata.get('source', 'Unknown')}")
                        # Show preview of document content (first 200 characters)
                        st.write(doc.page_content[:200] + "...")
            else:
                st.write("No local documents found.")
