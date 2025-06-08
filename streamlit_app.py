"""
Streamlit Web Application for GRI Disclosure Extraction

This web application provides an intuitive interface for extracting GRI disclosures 
from sustainability report PDFs using multiple detection strategies.

Author: Mohammad Habibul Akhyar
Date: 8 June 2025
"""

import streamlit as st
import pandas as pd
import json
import time
import os
from typing import Dict, List, Any, Optional
from extractGRI import GRIExtractor
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="GRI Disclosure Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def get_status_emoji(coverage: float) -> tuple:
    """Get status emoji and color based on coverage percentage."""
    if coverage >= 90:
        return "🟢", "EXCELLENT", "success"
    elif coverage >= 70:
        return "🟡", "GOOD", "warning"
    elif coverage >= 50:
        return "🟠", "FAIR", "info"
    else:
        return "🔴", "POOR", "error"

def display_extraction_summary(results: Dict[str, List[Dict[str, str]]], duration: float):
    """Display extraction summary with metrics and status."""
    total_codes = len(results["gri_disclosures"])
    found_codes = sum(1 for item in results["gri_disclosures"] if item["status"] and item["status"].lower() == "yes")
    coverage = found_codes / total_codes * 100 if total_codes > 0 else 0
    
    emoji, status_text, status_type = get_status_emoji(coverage)
    
    st.subheader("📊 GRI Extraction Summary")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⏱️ Processing Time",
            value=format_duration(duration)
        )
    
    with col2:
        st.metric(
            label="🎯 Total GRI Codes",
            value=total_codes
        )
    
    with col3:
        st.metric(
            label="✅ Found GRI Codes",
            value=found_codes,
            delta=f"{coverage:.1f}%"
        )
    
    with col4:
        st.metric(
            label="📈 Coverage Rate",
            value=f"{coverage:.1f}%"
        )
    
    # Status indicator
    if status_type == "success":
        st.success(f"🏆 Extraction Quality: {emoji} {status_text}")
    elif status_type == "warning":
        st.warning(f"🏆 Extraction Quality: {emoji} {status_text}")
    elif status_type == "info":
        st.info(f"🏆 Extraction Quality: {emoji} {status_text}")
    else:
        st.error(f"🏆 Extraction Quality: {emoji} {status_text}")

def create_coverage_chart(results: Dict[str, List[Dict[str, str]]]):
    """Create coverage chart by GRI standard."""
    # Group by material topic
    topic_stats = {}
    for item in results["gri_disclosures"]:
        topic = item["material_topic"]
        if topic not in topic_stats:
            topic_stats[topic] = {"total": 0, "found": 0}
        topic_stats[topic]["total"] += 1
        if item["status"] and item["status"].lower() == "yes":
            topic_stats[topic]["found"] += 1
      # Calculate coverage percentages
    chart_data = []
    for topic, stats in topic_stats.items():
        coverage = (stats["found"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        chart_data.append({
            "GRI Standard": topic.replace("GRI ", ""),
            "Coverage %": coverage,
            "Found": stats["found"],
            "Total": stats["total"]
        })
    
    if not chart_data:
        # Return empty figure if no data
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for chart",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    df_chart = pd.DataFrame(chart_data)
    df_chart = df_chart.sort_values("Coverage %", ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        df_chart,
        x="Coverage %",
        y="GRI Standard",
        orientation="h",
        color="Coverage %",
        color_continuous_scale="RdYlGn",
        title="📈 GRI Coverage by Standard",
        hover_data=["Found", "Total"],
        height=max(400, len(df_chart) * 25)
    )
    
    fig.update_layout(
        xaxis_title="Coverage Percentage (%)",
        yaxis_title="GRI Standard",
        coloraxis_colorbar_title="Coverage %",
        showlegend=False
    )
    
    return fig

def display_results_table(results: Dict[str, List[Dict[str, str]]]):
    """Display results in an interactive table."""
    st.subheader("📋 Detailed GRI Disclosure Results")
    
    # Convert to DataFrame
    df = pd.DataFrame(results["gri_disclosures"])
    
    # Handle null status values - convert to string for consistent processing
    df["status"] = df["status"].fillna("none").astype(str)
    
    # Add status indicators
    def get_status_icon(status):
        if pd.isna(status) or status.lower() in ["none", "nan", ""]:
            return "❌"
        return "✅" if status.lower() == "yes" else "❌"
    
    df["Status Icon"] = df["status"].apply(get_status_icon)
    
    # Create a clean status column for filtering
    df["Status_Clean"] = df["status"].apply(lambda x: "Found" if str(x).lower() == "yes" else "Not Found")
    
    # Reorder columns
    df = df[["Status Icon", "gri_code", "material_topic", "status", "Status_Clean", "description"]]
    df.columns = ["Status", "GRI Code", "Material Topic", "Found", "Status_Clean", "Description"]
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status:",
            options=["All", "Found Only", "Not Found Only"],
            key="status_filter"
        )
    
    with col2:
        # Get unique topics and clean them up
        unique_topics = sorted([topic for topic in df["Material Topic"].unique() if pd.notna(topic)])
        topic_filter = st.selectbox(
            "Filter by GRI Standard:",
            options=["All"] + unique_topics,
            key="topic_filter"
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply status filter
    if status_filter == "Found Only":
        filtered_df = filtered_df[filtered_df["Status_Clean"] == "Found"]
    elif status_filter == "Not Found Only":
        filtered_df = filtered_df[filtered_df["Status_Clean"] == "Not Found"]
    
    # Apply topic filter
    if topic_filter != "All":
        filtered_df = filtered_df[filtered_df["Material Topic"] == topic_filter]
      # Remove the helper column before display
    display_df = filtered_df.drop(columns=["Status_Clean"])
    
    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(width="small"),
            "GRI Code": st.column_config.TextColumn(width="small"),
            "Material Topic": st.column_config.TextColumn(width="large"),
            "Found": st.column_config.TextColumn(width="small"),
            "Description": st.column_config.TextColumn(width="large")
        }
    )
    
    # Display filter summary
    st.caption(f"Showing {len(display_df)} of {len(df)} total GRI disclosures")

def main():
    """Main Streamlit application."""
    st.title("📊 GRI Disclosure Extractor")
    st.markdown("Extract GRI (Global Reporting Initiative) disclosures from sustainability report PDFs")
    
    # Initialize session state for results
    if 'extraction_results' not in st.session_state:
        st.session_state.extraction_results = None
    if 'extraction_duration' not in st.session_state:
        st.session_state.extraction_duration = None
    if 'processed_filename' not in st.session_state:
        st.session_state.processed_filename = None
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Method selection
    extraction_method = st.sidebar.selectbox(
        "🔍 Extraction Method:",
        options=[
            "Auto (Pattern Match → TF-IDF → LLM)",
            "Pattern Matching Only",
            "TF-IDF Similarity Only",
            "LLM Analysis Only"
        ],
        help="Choose the extraction strategy to use"
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("✅ **Best Method Recommendation**")
    st.sidebar.markdown("- **TF-IDF Similarity** provides the best balance of accuracy and speed. It is especially effective for diverse document formats.")

    # Optional Groq API key
    use_llm = st.sidebar.checkbox(
        "🤖 Enable LLM Fallback",
        value=False,
        help="Enable Groq LLM as fallback for difficult cases"
    )
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if use_llm or "LLM" in extraction_method:
        # Show current status
        if groq_api_key:
            st.sidebar.success("✅ Groq API key loaded from environment")
            # Option to override with manual input
            override_key = st.sidebar.text_input(
                "🔑 Override Groq API Key (optional):",
                type="password",
                help="Leave empty to use environment variable",
                placeholder="Using environment variable"
            )
            if override_key:
                groq_api_key = override_key
        else:
            st.sidebar.warning("⚠️ No API key found in environment")
            groq_api_key = st.sidebar.text_input(
                "🔑 Groq API Key:",
                type="password",
                help="Enter your Groq API key for LLM analysis"
            )
        
        if not groq_api_key and ("LLM" in extraction_method):
            st.sidebar.error("❌ Groq API key required for LLM analysis")
            st.sidebar.info("💡 Tip: Add GROQ_API_KEY to your .env file")


    # File upload
    st.header("📄 Upload Sustainability Report PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a sustainability report PDF to extract GRI disclosures"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Display file info
        file_size = len(uploaded_file.getbuffer()) / (1024 * 1024)  # MB
        st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size:.1f} MB)")
        
        # Extract button
        if st.button("🚀 Extract GRI Disclosures", type="primary"):
            try:
                with st.spinner("🔄 Processing PDF and extracting GRI disclosures..."):
                    start_time = time.time()
                    
                    # Initialize extractor
                    extractor = GRIExtractor(groq_api_key=groq_api_key)
                    
                    # Extract text from PDF
                    pages_data = extractor.extract_text_from_pdf(temp_path)
                    
                    if not pages_data:
                        st.error("❌ Failed to extract text from PDF")
                        return
                    
                    st.info(f"📖 Extracted text from {len(pages_data)} pages")
                    
                    # Detect GRI section based on selected method
                    gri_start_page = None
                    
                    if extraction_method == "Pattern Matching Only":
                        gri_start_page = extractor.detect_gri_section_pattern_matching(pages_data)
                    elif extraction_method == "TF-IDF Similarity Only":
                        gri_start_page = extractor.detect_gri_section_tfidf(pages_data)
                    elif extraction_method == "LLM Analysis Only":
                        if groq_api_key:
                            gri_start_page = extractor.detect_gri_section_llm(pages_data)
                        else:
                            st.error("❌ Groq API key required for LLM analysis")
                            return
                    else:  # Auto method
                        # Try pattern matching first
                        gri_start_page = extractor.detect_gri_section_pattern_matching(pages_data)
                        
                        # Fallback to TF-IDF
                        if gri_start_page is None:
                            st.info("🔄 Pattern matching failed, trying TF-IDF...")
                            gri_start_page = extractor.detect_gri_section_tfidf(pages_data)
                          # Fallback to LLM if enabled
                        if gri_start_page is None and groq_api_key:
                            st.info("🔄 TF-IDF failed, trying LLM...")
                            gri_start_page = extractor.detect_gri_section_llm(pages_data)
                    
                    if gri_start_page is None:
                        st.warning("⚠️ Could not detect GRI section using selected method")
                        results = extractor._create_empty_result()
                    else:
                        st.success(f"✅ Found GRI section starting at page {gri_start_page}")
                        
                        # Extract GRI codes
                        gri_status = extractor.extract_gri_codes_from_section(pages_data, gri_start_page)
                        results = extractor._format_results(gri_status)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                      # Store results in session state
                    st.session_state.extraction_results = results
                    st.session_state.extraction_duration = duration
                    st.session_state.processed_filename = uploaded_file.name
                
            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Display results (outside the extraction button block for persistence)
    if st.session_state.extraction_results is not None:
        results = st.session_state.extraction_results
        duration = st.session_state.extraction_duration
        processed_filename = st.session_state.processed_filename
        
        st.header("🎯 Extraction Results")
        
        # Summary metrics
        display_extraction_summary(results, duration)
        
        # Coverage chart
        st.subheader("📊 Coverage Analysis")
        fig = create_coverage_chart(results)
        st.plotly_chart(fig, use_container_width=True)
        
        # Results table
        display_results_table(results)
        
        # Download options
        st.header("💾 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_str = json.dumps(results, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"gri_results_{processed_filename.replace('.pdf', '')}.json",
                mime="application/json",
                key="download_json"
            )
        
        with col2:
            # CSV download
            df_download = pd.DataFrame(results["gri_disclosures"])
            csv_str = df_download.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_str,
                file_name=f"gri_results_{processed_filename.replace('.pdf', '')}.csv",
                mime="text/csv",
                key="download_csv"
            )
    
    # Information section
    with st.expander("ℹ️ About GRI Extraction Methods"):
        st.markdown("""
        ### Extraction Methods:
        
        **🔍 Pattern Matching**
        - Searches for specific GRI-related keywords and patterns
        - Fast and reliable for well-formatted documents
        - Best for documents with clear GRI section headers
        
        **📊 TF-IDF Similarity**
        - Uses machine learning to find semantically similar content
        - Good for documents with varied formatting
        - Analyzes text similarity to GRI-related terms
        
        **🤖 LLM Analysis**
        - Uses advanced AI to understand document structure
        - Most flexible but requires API key
        - Best for complex or non-standard documents
        
        **⚡ Auto Mode**
        - Tries methods in sequence: Pattern → TF-IDF → LLM
        - Recommended for best results
        - Balances speed and accuracy
        """)
    
    with st.expander("📋 Supported GRI Standards"):
        st.markdown("""
        This tool supports extraction of **134 GRI disclosure codes** across:
        
        - **GRI 2**: General Disclosures 2021 (30 codes)
        - **GRI 3**: Material Topics 2021 (3 codes)
        - **GRI 101**: Biodiversity 2024 (8 codes)
        - **Economic Standards**: GRI 201-207 (16 codes)
        - **Environmental Standards**: GRI 301-308 (33 codes)
        - **Social Standards**: GRI 401-418 (44 codes)
        """)

if __name__ == "__main__":
    main()
