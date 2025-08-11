import streamlit as st
import tempfile
import os
from datetime import datetime
import json
import time

from fixed_agents import TranscriptionAgent, AnalysisAgent

st.set_page_config(
    page_title="MeetingMind AI",
    page_icon="⚡",
    layout="wide"
)

# Fixed CSS - make dropdown dark with white text, fix input sources
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    font-family: 'Inter', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Fix sidebar background */
section[data-testid="stSidebar"] {
    background: #1e293b !important;
}

/* Make ALL sidebar text white */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Fix the dropdown box itself */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #334155 !important;
    color: #ffffff !important;
    border: 1px solid #64748b !important;
    border-radius: 8px !important;
}

/* Fix dropdown when clicked */
section[data-testid="stSidebar"] .stSelectbox ul {
    background: #334155 !important;
    border: 1px solid #64748b !important;
}

section[data-testid="stSidebar"] .stSelectbox li {
    background: #334155 !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stSelectbox li:hover {
    background: #3b82f6 !important;
}

/* Style checkboxes properly */
section[data-testid="stSidebar"] .stCheckbox > div {
    background: rgba(59, 130, 246, 0.1);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border: 1px solid rgba(59, 130, 246, 0.3);
    transition: all 0.3s ease;
}

section[data-testid="stSidebar"] .stCheckbox > div:hover {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.6);
}

/* Professional buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    transform: translateY(-1px);
}

/* Section headers */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #3b82f6;
}

/* Input styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(51, 65, 85, 0.8) !important;
    border: 1px solid #64748b !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

/* Action items */
.action-item {
    background: rgba(51, 65, 85, 0.6);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid #64748b;
    transition: all 0.3s ease;
}

.action-item:hover {
    background: rgba(51, 65, 85, 0.8);
    border-color: #3b82f6;
    transform: translateY(-2px);
}

.priority-high { border-left: 4px solid #ef4444; }
.priority-medium { border-left: 4px solid #f59e0b; }
.priority-low { border-left: 4px solid #22c55e; }

/* Status indicators */
.status-indicator {
    display: inline-flex;
    align-items: center;
    background: rgba(34, 197, 94, 0.1);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    border: 1px solid rgba(34, 197, 94, 0.3);
    margin: 1rem 0;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;
    background: #22c55e;
}

/* Progress bars */
.progress-container {
    background: rgba(51, 65, 85, 0.8);
    border-radius: 8px;
    height: 6px;
    margin: 1rem 0;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    transition: width 0.4s ease;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(51, 65, 85, 0.8);
    border-radius: 8px;
    padding: 0.25rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #94a3b8;
    font-weight: 500;
    border-radius: 6px;
}

.stTabs [aria-selected="true"] {
    background: #3b82f6;
    color: white;
    font-weight: 600;
}

.stMarkdown, .stText, p, div { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

def create_status_indicator(status, text):
    return f"""
    <div class="status-indicator">
        <span class="status-dot"></span>
        <span style="color: #ffffff; font-weight: 500;">{text}</span>
    </div>
    """

def create_progress_bar(percentage):
    return f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%;"></div>
    </div>
    """

def main():
    st.markdown('<h1 style="font-size: 3rem; color: #ffffff; text-align: center; margin-bottom: 0.5rem;">MeetingMind AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; text-align: center; margin-bottom: 2rem;">Transform meetings into actionable insights</p>', unsafe_allow_html=True)
    
    try:
        if 'transcription_agent' not in st.session_state:
            st.session_state.transcription_agent = TranscriptionAgent()
        if 'analysis_agent' not in st.session_state:
            st.session_state.analysis_agent = AnalysisAgent()
        st.markdown(create_status_indicator("success", "AI systems operational"), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"System failed: {e}")
        st.stop()
    
    with st.sidebar:
        st.markdown("# Control Panel")
        
        st.markdown("## Input Sources")
        use_audio = st.checkbox("Audio/Video Files", value=False)
        use_text = st.checkbox("Text Transcripts", value=True)
        use_notes = st.checkbox("Additional Context", value=False)
        
        st.markdown("---")
        
        st.markdown("## Settings")
        meeting_type = st.selectbox("Meeting Type", ["general", "standup", "planning", "retrospective"])
        
        st.markdown("---")
        st.markdown("## System Status")
        st.success("Connected")
        st.success("Ready")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        transcript = None
        user_notes = None
        audio_transcript = None
        
        if use_audio:
            st.markdown('<div class="section-header">Audio Processing</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Select meeting recording",
                type=['mp3', 'wav', 'm4a', 'mp4', 'mov', 'avi', 'mpeg']
            )
            
            if uploaded_file is not None:
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size / (1024*1024):.1f}MB")
                
                if st.button("Process Recording", type="primary"):
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    steps = [
                        ("Validating file format", 25),
                        ("Transcribing audio content", 75),
                        ("Finalizing transcript", 100)
                    ]
                    
                    for step_text, progress in steps:
                        status_placeholder.markdown(create_status_indicator("processing", step_text), unsafe_allow_html=True)
                        progress_placeholder.markdown(create_progress_bar(progress), unsafe_allow_html=True)
                        time.sleep(0.8)
                    
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        with open(tmp_file_path, 'rb') as audio_file:
                            audio_transcript = st.session_state.transcription_agent.transcribe_audio(audio_file)
                        
                        os.unlink(tmp_file_path)
                        
                        progress_placeholder.empty()
                        status_placeholder.markdown(create_status_indicator("success", "Processing completed successfully"), unsafe_allow_html=True)
                        st.session_state.audio_transcript = audio_transcript
                        
                    except Exception as e:
                        progress_placeholder.empty()
                        status_placeholder.error(f"Processing failed: {str(e)}")
            
            if 'audio_transcript' in st.session_state:
                with st.expander("View Audio Transcription"):
                    st.text_area("Transcribed Content", st.session_state.audio_transcript, height=150, disabled=True)
        
        if use_text:
            st.markdown('<div class="section-header">Text Input</div>', unsafe_allow_html=True)
            transcript = st.text_area(
                "Meeting Transcript",
                height=180,
                placeholder="Enter or paste meeting transcript here..."
            )
        
        if use_notes:
            st.markdown('<div class="section-header">Additional Context</div>', unsafe_allow_html=True)
            user_notes = st.text_area(
                "Context Notes",
                height=180,
                placeholder="Add meeting context or observations..."
            )
    
    with col2:
        st.markdown('<div class="section-header">Analytics Dashboard</div>', unsafe_allow_html=True)
        
        if st.session_state.get('last_analysis'):
            analysis = st.session_state.last_analysis
            
            st.metric("Action Items", len(analysis.get('action_items', [])))
            st.metric("Key Decisions", len(analysis.get('key_decisions', [])))
            st.metric("Blockers", len(analysis.get('blockers', [])))
            st.metric("Confidence", analysis.get('confidence_score', 'High'))
        else:
            st.info("Analytics will appear here after processing meeting data")
    
    # Analysis engine
    combined_content = ""
    sources_used = []
    
    if 'audio_transcript' in st.session_state and st.session_state.audio_transcript:
        combined_content += f"AUDIO TRANSCRIPTION:\n{st.session_state.audio_transcript}\n\n"
        sources_used.append("Audio Recording")
    
    if transcript and transcript.strip():
        combined_content += f"MEETING TRANSCRIPT:\n{transcript}\n\n"
        sources_used.append("Text Transcript")
    
    if user_notes and user_notes.strip():
        combined_content += f"ADDITIONAL CONTEXT:\n{user_notes}\n\n"
        sources_used.append("Context Notes")
    
    if combined_content.strip():
        st.markdown('<div class="section-header">Analysis Engine</div>', unsafe_allow_html=True)
        
        col_info, col_preview = st.columns([1, 1])
        with col_info:
            st.write(f"**Active Sources:** {len(sources_used)}")
            for i, source in enumerate(sources_used, 1):
                st.write(f"**{i}.** {source}")
        
        with col_preview:
            with st.expander("Preview Combined Input"):
                preview = combined_content[:400] + "..." if len(combined_content) > 400 else combined_content
                st.text_area("Content Preview", preview, height=120, disabled=True)
        
        if st.button("Analyze Meeting", type="primary", use_container_width=True):
            analysis_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            steps = [
                ("Processing input data", 20),
                ("Loading AI models", 40),
                ("Analyzing content", 60),
                ("Extracting insights", 80),
                ("Finalizing results", 100)
            ]
            
            for step_text, progress in steps:
                analysis_placeholder.markdown(create_status_indicator("processing", step_text), unsafe_allow_html=True)
                progress_placeholder.markdown(create_progress_bar(progress), unsafe_allow_html=True)
                time.sleep(1.0)
            
            try:
                analysis = st.session_state.analysis_agent.analyze_meeting_multi_source(
                    combined_content, meeting_type, sources_used
                )
                
                st.session_state.last_analysis = analysis
                st.session_state.sources_used = sources_used
                
                progress_placeholder.empty()
                analysis_placeholder.markdown(create_status_indicator("success", "Analysis completed successfully"), unsafe_allow_html=True)
                
                display_results(analysis, sources_used)
                
            except Exception as e:
                progress_placeholder.empty()
                analysis_placeholder.error(f"Analysis failed: {str(e)}")
    
    elif use_audio or use_text or use_notes:
        st.info("Add meeting content to your selected input sources above, then click analyze")

def display_results(analysis, sources_used):
    st.markdown('<div class="section-header">Analysis Results</div>', unsafe_allow_html=True)
    
    if sources_used:
        st.success(f"Successfully processed {len(sources_used)} data sources")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Executive Summary", "Action Items", "Decisions & Next Steps", "Export Options"])
    
    with tab1:
        st.markdown("### Meeting Summary")
        st.write(analysis['meeting_summary'])
        
        if analysis['attendees']:
            st.markdown("### Participants")
            participants = " • ".join(analysis['attendees'])
            st.write(f"**Attendees:** {participants}")
        
        if analysis.get('notes_insights'):
            st.markdown("### Key Insights")
            for insight in analysis['notes_insights']:
                st.write(f"• {insight}")
    
    with tab2:
        st.markdown("### Action Items")
        
        if analysis['action_items']:
            for i, item in enumerate(analysis['action_items'], 1):
                priority_class = f"priority-{item['priority'].lower()}"
                
                st.markdown(f'''
                <div class="action-item {priority_class}">
                    <h4 style="color: #3b82f6; margin-bottom: 1rem;">Task {i}: {item['task']}</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                        <div><strong>Assignee:</strong><br>{item['assignee']}</div>
                        <div><strong>Due Date:</strong><br>{item['due_date']}</div>
                        <div><strong>Priority:</strong><br>{item['priority']}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No action items identified in the meeting content")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Key Decisions")
            if analysis['key_decisions']:
                for i, decision in enumerate(analysis['key_decisions'], 1):
                    st.markdown(f"**{i}.** {decision}")
            else:
                st.info("No key decisions recorded")
        
        with col2:
            st.markdown("### Next Steps")
            if analysis.get('next_steps'):
                for step in analysis['next_steps']:
                    st.write(f"• {step}")
            else:
                st.info("No next steps specified")
        
        if analysis.get('blockers'):
            st.markdown("### Identified Blockers")
            for i, blocker in enumerate(analysis['blockers'], 1):
                st.warning(f"**Blocker {i}:** {blocker}")
    
    with tab4:
        st.markdown("### Export & Integration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_content = generate_email_summary(analysis)
            st.download_button(
                "Download Email Summary",
                email_content,
                file_name=f"meeting_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            json_content = json.dumps(analysis, indent=2)
            st.download_button(
                "Download JSON Data",
                json_content,
                file_name=f"meeting_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )

def generate_email_summary(analysis):
    timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    
    email_content = f"""Subject: Meeting Summary and Action Items - {timestamp}

Team,

Please find the meeting analysis summary below:

EXECUTIVE SUMMARY
{analysis['meeting_summary']}

PARTICIPANTS
{', '.join(analysis.get('attendees', ['Not specified']))}"""
    
    if analysis.get('key_decisions'):
        email_content += "\n\nKEY DECISIONS"
        for i, decision in enumerate(analysis['key_decisions'], 1):
            email_content += f"\n{i}. {decision}"
    
    if analysis.get('action_items'):
        email_content += "\n\nACTION ITEMS"
        for i, item in enumerate(analysis['action_items'], 1):
            email_content += f"""
{i}. {item['task']}
   → Assigned to: {item['assignee']}
   → Due date: {item['due_date']}
   → Priority: {item['priority']}
"""
    
    if analysis.get('next_steps'):
        email_content += "\n\nNEXT STEPS"
        for i, step in enumerate(analysis['next_steps'], 1):
            email_content += f"\n{i}. {step}"
    
    if analysis.get('blockers'):
        email_content += "\n\nBLOCKERS"
        for i, blocker in enumerate(analysis['blockers'], 1):
            email_content += f"\n{i}. {blocker}"
    
    email_content += f"""

Best regards,
MeetingMind AI Analysis System

Generated on {timestamp}
"""
    
    return email_content

if __name__ == "__main__":
    main()