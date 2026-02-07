"""
Multi-Agent Document Intelligence System - Streamlit UI
"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import DocumentOrchestrator
from utils.config import Config
from utils.output_formatter import OutputFormatter
from utils.document_processor import DocumentProcessor

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Document Intelligence",
    page_icon="📄",
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
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-pending {
        background-color: #f0f0f0;
        color: #666;
    }
    .status-processing {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-complete {
        background-color: #d4edda;
        color: #155724;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'agent_status' not in st.session_state:
        st.session_state.agent_status = {
            'summary': 'pending',
            'action': 'pending',
            'risk': 'pending'
        }


def update_agent_status(agent_name: str, status: str):
    """Callback to update agent processing status"""
    st.session_state.agent_status[agent_name] = status


def display_header():
    """Display application header"""
    st.markdown('<div class="main-header">📄 Multi-Agent Document Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Advanced AI-powered document analysis with specialized agents</div>', unsafe_allow_html=True)


def display_sidebar():
    """Display sidebar with configuration and info"""
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This system uses **three specialized AI agents** to analyze documents:
        
        **🔍 Summary Agent**
        - Generates context-aware summaries
        - Extracts key decisions and constraints
        - Preserves document intent
        
        **✅ Action Agent**
        - Identifies actionable tasks
        - Extracts owners and deadlines
        - Maps task dependencies
        
        **⚠️ Risk Agent**
        - Identifies potential risks
        - Flags open questions
        - Detects assumptions
        """)
        
        st.divider()
        
        st.header("⚙️ Configuration")
        config = Config()
        
        if config.validate():
            st.success("✓ Configuration valid")
            st.info(f"**Model:** {config.model_name}")
        else:
            st.error("⚠️ Missing API configuration")
            st.warning("Please set up your `.env` file with API keys")
        
        st.divider()
        
        st.header("📊 System Info")
        st.metric("Chunk Size", f"{config.chunk_size} tokens")
        st.metric("Chunk Overlap", f"{config.chunk_overlap} tokens")


def display_input_section():
    """Display document input section"""
    st.header("📤 Input Document")
    
    input_method = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload File"],
        horizontal=True
    )
    
    document_text = None
    
    if input_method == "Paste Text":
        document_text = st.text_area(
            "Paste your document here:",
            height=300,
            placeholder="Enter meeting transcript, project brief, or any document (500+ words recommended)..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=['txt', 'md', 'pdf', 'docx'],
            help="Supports TXT, MD, PDF, and DOCX files"
        )
        
        if uploaded_file:
            file_extension = Path(uploaded_file.name).suffix.lower()
            processor = DocumentProcessor()
            
            if file_extension == '.pdf':
                with st.spinner("Extracting text from PDF..."):
                    document_text = processor.read_pdf(uploaded_file)
            elif file_extension == '.docx':
                with st.spinner("Extracting text from DOCX..."):
                    document_text = processor.read_docx(uploaded_file)
            else:
                document_text = uploaded_file.read().decode('utf-8')
            
            if "Error reading" in document_text:
                st.error(document_text)
                document_text = None
            else:
                st.success(f"✓ Loaded {len(document_text.split())} words from {uploaded_file.name}")
    
    return document_text


def display_processing_status():
    """Display real-time processing status"""
    st.header("⚙️ Processing Status")
    
    col1, col2, col3 = st.columns(3)
    
    status_icons = {
        'pending': '⏳',
        'processing': '🔄',
        'complete': '✅'
    }
    
    status_labels = {
        'pending': 'Pending',
        'processing': 'Processing...',
        'complete': 'Complete'
    }
    
    with col1:
        status = st.session_state.agent_status['summary']
        st.markdown(f"""
        <div class="status-box status-{status}">
            <strong>{status_icons[status]} Summary Agent</strong><br/>
            {status_labels[status]}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status = st.session_state.agent_status['action']
        st.markdown(f"""
        <div class="status-box status-{status}">
            <strong>{status_icons[status]} Action Agent</strong><br/>
            {status_labels[status]}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status = st.session_state.agent_status['risk']
        st.markdown(f"""
        <div class="status-box status-{status}">
            <strong>{status_icons[status]} Risk Agent</strong><br/>
            {status_labels[status]}
        </div>
        """, unsafe_allow_html=True)


def display_results():
    """Display analysis results"""
    if not st.session_state.results:
        return
    
    results = st.session_state.results
    formatter = OutputFormatter()
    
    # Display summary statistics
    st.header("📊 Analysis Summary")
    stats = formatter.create_summary_stats(
        results['summary'],
        results['actions'],
        results['risks']
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Action Items", stats['total_actions'])
    with col2:
        st.metric("Risks Identified", stats['total_risks'])
    with col3:
        st.metric("Open Questions", stats['total_open_questions'])
    with col4:
        st.metric("Key Decisions", stats['key_decisions'])
    
    st.divider()
    
    # Tabbed results display
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "✅ Actions", "⚠️ Risks", "📄 Raw JSON"])
    
    with tab1:
        st.markdown("### Document Summary")
        summary_text = formatter.format_summary_for_display(results['summary'])
        st.markdown(summary_text)
    
    with tab2:
        st.markdown("### Action Items")
        if results['actions']:
            df = formatter.format_actions_as_dataframe(results['actions'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No action items identified")
    
    with tab3:
        st.markdown("### Risks & Open Issues")
        risks_text = formatter.format_risks_for_display(results['risks'])
        st.markdown(risks_text)
    
    with tab4:
        st.markdown("### Complete Results (JSON)")
        st.json(results, expanded=False)
    
    # Export options
    st.divider()
    st.header("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        json_str = formatter.export_to_json(results)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"document_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        if results['actions']:
            csv_str = formatter.export_actions_to_csv(results['actions'])
            st.download_button(
                label="📥 Download Actions (CSV)",
                data=csv_str,
                file_name=f"action_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def main():
    """Main application logic"""
    initialize_session_state()
    
    display_header()
    display_sidebar()
    
    # Input section
    document_text = display_input_section()
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button(
            "🚀 Process Document",
            type="primary",
            use_container_width=True,
            disabled=not document_text or len(document_text.strip()) < 100
        )
    
    if not document_text or len(document_text.strip()) < 100:
        st.info("💡 Please enter at least 100 characters to process")
    
    # Process document
    if process_button and document_text:
        st.session_state.processing = True
        st.session_state.agent_status = {
            'summary': 'pending',
            'action': 'pending',
            'risk': 'pending'
        }
        
        # Display processing status
        status_placeholder = st.empty()
        
        with status_placeholder.container():
            display_processing_status()
        
        try:
            # Initialize orchestrator
            config = Config()
            orchestrator = DocumentOrchestrator(config)
            
            # Validate configuration
            is_valid, error_msg = orchestrator.validate_configuration()
            if not is_valid:
                st.error(f"❌ Configuration Error: {error_msg}")
                st.stop()
            
            # Process document with progress updates
            with st.spinner("Processing document..."):
                results = orchestrator.process_document(
                    document_text,
                    progress_callback=update_agent_status
                )
            
            st.session_state.results = results
            st.session_state.processing = False
            
            # Update status display
            with status_placeholder.container():
                display_processing_status()
            
            st.success("✅ Document processed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")
            st.exception(e)
            st.session_state.processing = False
    
    # Display results if available
    if st.session_state.results:
        st.divider()
        display_results()


if __name__ == "__main__":
    main()
