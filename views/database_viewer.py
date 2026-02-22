"""ChromaDB Knowledge Base Inspector View.

This module provides a Streamlit-based interface for inspecting and managing
the ChromaDB vector database. It displays stored document chunks, metadata,
statistics, and provides database management capabilities.
"""

from typing import Any
import streamlit as st
import pandas as pd
import chromadb

# Configure Streamlit page settings
st.set_page_config(page_title="ChromaDB Inspector", layout="wide")
st.title("Knowledge Base Inspector")

# ChromaDB persistence directory path
DB_PATH: str = "/app/chroma_db"

try:
    # Initialize ChromaDB persistent client
    client: chromadb.PersistentClient = chromadb.PersistentClient(path=DB_PATH)
    collections: list[chromadb.Collection] = client.list_collections()

    if not collections:
        st.warning("No data found. Sync your knowledge on the Main App first!")
    else:
        # Collection selector dropdown
        col_name: str = st.selectbox(
            "Select Collection:",
            [c.name for c in collections]
        )
        selected_col: chromadb.Collection = client.get_collection(col_name)
        
        # Retrieve all documents from selected collection
        data: dict[str, Any] = selected_col.get()
        
        # Create DataFrame for display
        df: pd.DataFrame = pd.DataFrame({
            "ID": data["ids"],
            "Source": [m.get("source", "N/A") for m in data["metadatas"]],
            "Content Snippet": [doc[:300] + "..." for doc in data["documents"]]
        })

        # Display key metrics in three columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", len(df))
        with col2:
            unique_sources: int = df["Source"].nunique()
            st.metric("Unique Pages", unique_sources)
        with col3:
            avg_length: float = df["Content Snippet"].str.len().mean()
            st.metric("Avg Chunk Size", f"{int(avg_length)} chars")
        
        # Display data table with full width
        st.dataframe(df, use_container_width=True)
        
        # Additional statistics in expandable section
        with st.expander("📊 Detailed Statistics"):
            st.write("**Top 10 Most Chunked Pages:**")
            source_counts: pd.Series = df["Source"].value_counts().head(10)
            st.bar_chart(source_counts)
            
            st.write("**Sample Sources:**")
            for source in df["Source"].unique()[:5]:
                st.text(source)

        # Database management: wipe collection button
        if st.button("🗑️ Wipe Database"):
            client.delete_collection(col_name)
            st.rerun()

except Exception as e:
    st.error(f"Error loading ChromaDB: {e}")