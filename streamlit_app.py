import streamlit as st
import pandas as pd
import json
import time
import os
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the GRI extractor
from extractGRI import GRIExtractor

# Page configuration
st.set_page_config(
    page_title="GRI Disclosure Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
    .sidebar-note {
        background-color: #2196f3;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2189;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def format_duration(seconds):
    """Format duration in seconds to human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def get_status_emoji(status):
    """Get emoji based on status."""
    if not status:
        return "❌"
    status_upper = str(status).upper()
    if status_upper == 'YES':
        return "✅"
    elif 'partial' in status_upper or 'incomplete' in status_upper:
        return "⚠️"
    else:
        return "❌"

def get_coverage_status(coverage_rate):
    """Get coverage status based on rate."""
    if coverage_rate >= 80:
        return "Excellent", "status-good", "🟢"
    elif coverage_rate >= 60:
        return "Good", "status-good", "🟡"
    elif coverage_rate >= 40:
        return "Fair", "status-warning", "🟠"
    else:
        return "Poor", "status-danger", "🔴"

def display_extraction_summary(results, processing_time):
    """Display extraction summary with metrics."""
    st.subheader("📊 Extraction Summary")
    
    # Calculate metrics
    total_codes = len(results)
    found_codes = len([r for r in results if r.get('status', '') and str(r.get('status', '')).upper() == 'YES'])
    coverage_rate = (found_codes / total_codes * 100) if total_codes > 0 else 0
    
    # Get coverage status
    coverage_text, coverage_class, coverage_emoji = get_coverage_status(coverage_rate)
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⏱️ Processing Time",
            value=format_duration(processing_time),
            help="Time taken to process the document"
        )
    
    with col2:
        st.metric(
            label="📋 Total GRI Codes",
            value=str(total_codes),
            help="Total number of GRI disclosure codes checked"
        )
    
    with col3:
        st.metric(
            label="✅ Found Codes",
            value=str(found_codes),
            delta=f"{found_codes - (total_codes - found_codes)}" if total_codes > 0 else None,
            help="Number of GRI codes successfully found/extracted"
        )
    
    with col4:
        st.metric(
            label=f"{coverage_emoji} Coverage Rate",
            value=f"{coverage_rate:.1f}%",
            help="Percentage of GRI codes found vs total codes"
        )
    
    # Coverage status indicator
    st.markdown(f"""
    <div class="metric-container">
        <h4>Coverage Assessment: <span class="{coverage_class}">{coverage_emoji} {coverage_text}</span></h4>
        <p>Your document covers <strong>{coverage_rate:.1f}%</strong> of the checked GRI disclosure codes.</p>
    </div>
    """, unsafe_allow_html=True)

def create_coverage_chart(results):
    """Create coverage chart using Plotly."""
    # Count statuses
    status_counts = {}
    for result in results:
        status = result.get('status', 'Not Found')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if not status_counts:
        return None
      # Create pie chart
    fig = px.pie(
        values=list(status_counts.values()),
        names=list(status_counts.keys()),
        title="GRI Code Status Distribution",
        color_discrete_map={
            'YES': '#28a745',
            'yes': '#28a745',
            'none': '#dc3545',
            'NONE': '#dc3545',
            'Not Found': '#dc3545',
            'Partial': '#ffc107',
            'Error': '#dc3545'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        height=400,
        margin=dict(t=50, b=0, l=0, r=0)
    )
    
    return fig

def display_results_table(results):
    """Display results in an interactive table."""
    st.subheader("📋 Detailed Results")
    
    if not results:
        st.warning("No results to display.")
        return None
    
    # Convert results to DataFrame
    df_data = []
    for result in results:
        df_data.append({
            'Material Topic': result.get('material_topic', 'N/A'),
            'GRI Code': result.get('gri_code', 'N/A'),
            'Status': result.get('status', 'Not Found'),
            'Status Icon': get_status_emoji(result.get('status', 'Not Found')),
            'Content Preview': str(result.get('content', 'N/A'))[:100] + "..." if result.get('content') and len(str(result.get('content'))) > 100 else str(result.get('content', 'N/A'))
        })
    
    df = pd.DataFrame(df_data)
    
    # Add filters
    # col1, col2 = st.columns(2)
    
    # with col1:
    status_filter = st.multiselect(
        "Filter by Status:",
        options=df['Status'].unique(),
        default=df['Status'].unique(),
    key="status_filter"
    )
    
    # with col2:
    topic_filter = st.multiselect(
        "Filter by Material Topic:",
        options=df['Material Topic'].unique(),
        default=df['Material Topic'].unique(),
        key="topic_filter"
    )
    
    # Apply filters
    filtered_df = df[
        (df['Status'].isin(status_filter)) & 
        (df['Material Topic'].isin(topic_filter))
    ]
    
    # Display filtered results count
    st.info(f"Showing {len(filtered_df)} of {len(df)} results")
    
    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400,
        column_config={
            'Status Icon': st.column_config.TextColumn('Status'),
            'Content Preview': st.column_config.TextColumn('Content Preview', width='large')
        }
    )
    
    return df

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 GRI Disclosure Extractor</h1>', unsafe_allow_html=True)
    st.markdown("**Extract and analyze GRI (Global Reporting Initiative) disclosures from PDF documents**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Method selection
        method = st.selectbox(
            "Extraction Method:",
            options=["Auto", "Pattern", "TF-IDF", "LLM"],
            index=2,  # Default to TF-IDF
            help="Choose the method for extracting GRI disclosures"
        )
        
        # Recommendation note
        st.markdown("""
        <div class="sidebar-note">
            <h4>💡 Recommendation</h4>
            <p>The <strong>TF-IDF method</strong> provides the best balance of accuracy and speed for most documents.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API Key status
        api_key = os.getenv('GROQ_API_KEY')
        if method == "LLM":
            if api_key:
                st.success("✅ GROQ API Key loaded")
            else:
                st.error("❌ GROQ API Key not found")
                st.info("Please add GROQ_API_KEY to your .env file for LLM method")
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            chunk_size = st.slider("Chunk Size", 500, 2000, 1000, 100, help="Text chunk size for processing")
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.1, help="Minimum confidence for extraction")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document containing GRI disclosures"
        )
    
    with col2:
        if uploaded_file:
            st.subheader("📄 File Info")
            st.info(f"**Filename:** {uploaded_file.name}")
            st.info(f"**Size:** {uploaded_file.size:,} bytes")
            st.info(f"**Type:** {uploaded_file.type}")
    
    # Process file    if uploaded_file is not None:
        if st.button("🚀 Extract GRI Disclosures", type="primary", use_container_width=True):
            temp_path = f"temp_{uploaded_file.name}"
            try:
                with st.spinner(f"Processing document using {method} method..."):
                    # Save uploaded file temporarily
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Initialize extractor
                    extractor = GRIExtractor()
                    
                    # Start timing
                    start_time = time.time()
                    
                    # Extract based on method
                    raw_results = extractor.extract_gri_disclosures(temp_path)
                    
                    # Convert results format for display
                    if 'gri_disclosures' in raw_results:
                        results = raw_results['gri_disclosures']
                    else:
                        results = raw_results
                    
                    # Calculate processing time
                    processing_time = time.time() - start_time
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                # Store results in session state
                st.session_state.results = results
                st.session_state.processing_time = processing_time
                st.session_state.method_used = method
                st.session_state.filename = uploaded_file.name
                
                st.success(f"✅ Extraction completed using {method} method!")
                
            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Display results if available
    if hasattr(st.session_state, 'results') and st.session_state.results:
        st.divider()
        
        # Display summary
        display_extraction_summary(st.session_state.results, st.session_state.processing_time)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Table View", "📊 Charts", "💾 Download"])
        
        with tab1:
            df = display_results_table(st.session_state.results)
        
        with tab2:
            st.subheader("📊 Coverage Analysis")
            fig = create_coverage_chart(st.session_state.results)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No chart data available")
        
        with tab3:
            st.subheader("💾 Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON download
                json_data = json.dumps(st.session_state.results, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_data,
                    file_name=f"gri_results_{st.session_state.filename}_{st.session_state.method_used}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # CSV download
                if 'df' in locals() and df is not None:
                    csv_buffer = BytesIO()
                    df.to_csv(csv_buffer, index=False, encoding='utf-8')
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_data,
                        file_name=f"gri_results_{st.session_state.filename}_{st.session_state.method_used}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # Summary info
            st.info(f"""
            **Export Summary:**
            - Method: {st.session_state.method_used}
            - Processing Time: {format_duration(st.session_state.processing_time)}
            - Total Results: {len(st.session_state.results)}
            - Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """)

if __name__ == "__main__":
    main()