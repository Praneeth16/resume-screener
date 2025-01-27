import os
import asyncio
import streamlit as st
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional, Tuple
import plotly.express as px
from dotenv import load_dotenv
import json

from resume_parser import (
    ResumeParser, 
    ResumeInfo, 
    ExtraCurricular,
    ExtraCurricularExtractor,
    save_resume_data,
    calculate_candidate_score
)

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stProgress .st-bo {
        background-color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .project-card {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'parsed_resume' not in st.session_state:
    st.session_state.parsed_resume = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Upload"

@st.cache_resource
def get_parser():
    """Initialize and cache the resume parser."""
    return ResumeParser(
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        base_url=os.getenv('DEEPSEEK_URL')
    )

# Create async function for parsing
async def async_parse_resume(file_content: bytes, file_name: str) -> Optional[Dict]:
    """Async function to parse resume."""
    temp_file = "temp_resume.pdf"
    with open(temp_file, "wb") as f:
        f.write(file_content)
    
    try:
        parser = get_parser()
        resume_info, extra_info, token_usage = await parser.parse_resume(temp_file)
        
        # Calculate scores
        scores = calculate_candidate_score(resume_info, extra_info)
        
        # Convert to dictionary for caching
        resume_dict = resume_info.model_dump()
        extra_dict = extra_info.model_dump()
        token_dict = {
            'completion_tokens': token_usage.completion_tokens,
            'prompt_tokens': token_usage.prompt_tokens,
            'total_tokens': token_usage.total_tokens,
            'cached_tokens': token_usage.cached_tokens,
            'scores': scores  # Add scores to response
        }
        
        return {
            'resume': resume_dict,
            'extra': extra_dict,
            'tokens': token_dict
        }
    except Exception as e:
        st.error(f"Error parsing resume: {str(e)}")
        return None
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Wrapper function for caching
@st.cache_data
def parse_resume_to_dict(file_content: bytes, file_name: str) -> Optional[Dict]:
    """Cached wrapper for resume parsing."""
    return asyncio.run(async_parse_resume(file_content, file_name))

def reconstruct_resume_info(data: Dict) -> Tuple[ResumeInfo, ExtraCurricular]:
    """Reconstruct ResumeInfo and ExtraCurricular from dictionary."""
    resume_info = ResumeInfo.model_validate(data['resume'])
    extra_info = ExtraCurricular.model_validate(data['extra'])
    return resume_info, extra_info

def display_token_usage(token_data: Dict):
    """Display token usage information."""
    st.sidebar.markdown("### Token Usage")
    st.sidebar.markdown(f"""
    - Completion Tokens: {token_data['completion_tokens']}
    - Prompt Tokens: {token_data['prompt_tokens']}
    - Total Tokens: {token_data['total_tokens']}
    """)

def display_metadata(metadata, scores):
    """Display student metadata and scores in a formatted way."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Personal Information")
        st.markdown(f"""
        <div class="metric-card">
            <h4>Name: {metadata.name}</h4>
            <p>Registration Number: {metadata.reg_no}</p>
            <p>Gender: {metadata.gender}</p>
            <p>Date of Birth: {metadata.dob}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Overall Score")
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Score: {scores['total_score']}/100</h4>
            <p>Academic Score: {scores['academic_score']}/20</p>
            <p>Technical Score: {scores['technical_score']}/35</p>
            <p>Projects Score: {scores['projects_score']}/30</p>
            <p>Extra-curricular Score: {scores['extra_score']}/15</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Contact Information")
        st.markdown(f"""
        <div class="metric-card">
            <p>Email: {metadata.email}</p>
            <p>Phone: {metadata.phone}</p>
            <p>Mobile: {metadata.mobile}</p>
            <p>Branch: {metadata.branch}</p>
            <p>Degree: {metadata.degree}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add score visualization
        st.markdown("### Score Breakdown")
        score_data = pd.DataFrame([{
            'Component': 'Academic',
            'Score': scores['academic_score'],
            'Max': 20
        }, {
            'Component': 'Technical',
            'Score': scores['technical_score'],
            'Max': 35
        }, {
            'Component': 'Projects',
            'Score': scores['projects_score'],
            'Max': 30
        }, {
            'Component': 'Extra-curricular',
            'Score': scores['extra_score'],
            'Max': 15
        }])
        
        fig = px.bar(score_data, 
                    x='Component', 
                    y=['Score', 'Max'],
                    title='Score Distribution',
                    barmode='overlay',
                    color_discrete_sequence=['#1f77b4', '#e0e0e0'])
        
        fig.update_layout(
            yaxis_title="Points",
            showlegend=True,
            legend_title="",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_academic_performance(academic_performance):
    """Display academic performance with a line chart."""
    st.markdown("### Academic Performance")
    
    # Create DataFrame for plotting
    df = pd.DataFrame([{
        'Semester': p.semester,
        'SGPA': p.sgpa,
        'CGPA': p.cgpa,
        'Duration': p.duration
    } for p in academic_performance])
    
    # Create line chart
    fig = px.line(df, x='Semester', y=['SGPA', 'CGPA'],
                  title='Academic Progress',
                  markers=True,
                  labels={'value': 'Grade Points', 'variable': 'Metric'})
    
    fig.update_layout(
        xaxis_title="Semester",
        yaxis_title="Grade Points",
        yaxis_range=[df.SGPA.min()-1, df.SGPA.max()+1],
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display tabular data
    st.dataframe(df, use_container_width=True)

def display_projects(projects):
    """Display projects in card format."""
    st.markdown("### Projects")
    
    for i, project in enumerate(projects):
        with st.container(border=True):
            st.markdown(f"""
            <div >
                <h4>{i+1}. {project.name}</h4>
                <p><strong>Company:</strong> {project.company}</p>
                <p><strong>Duration:</strong> {project.duration}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create skills dataframe
            skills_data = {
                'Programming': project.skill.programming_languages,
                'Frameworks': project.skill.frameworks,
                'Databases': project.skill.databases,
                'Other Technologies': project.skill.other_technologies,
                'Knowledge Area': project.skill.knowledge_area
            }
            
            # Filter out empty categories
            skills_data = {k: v for k, v in skills_data.items() if v}
            
            if skills_data:
                # Create a DataFrame with skills
                max_skills = max(len(v) for v in skills_data.values())
                # Pad lists to same length with empty strings
                skills_data = {k: v + [''] * (max_skills - len(v)) for k, v in skills_data.items()}
                df = pd.DataFrame(skills_data)
                
                # Display skills table with custom styling
                st.markdown("<p><strong>Skills:</strong></p>", unsafe_allow_html=True)
                styled_df = (
                    df.style
                    .hide(axis="index")
                    .format(lambda x: '' if pd.isna(x) else x)
                    .set_table_styles([
                        {'selector': 'th', 'props': [
                            ('text-align', 'left'),
                            ('font-size', '14px'),
                            ('padding', '5px'),
                            ('background-color', '#f0f2f6')
                        ]},
                        {'selector': 'td', 'props': [
                            ('text-align', 'left'),
                            ('font-size', '14px'),
                            ('padding', '5px')
                        ]}
                    ])
                )
                st.dataframe(styled_df, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

def display_skills_summary(projects):
    """Display aggregated skills from all projects."""
    st.markdown("### Overall Skills Profile")
    
    # Aggregate skills
    all_skills = {
        'Programming': set(),
        'Frameworks': set(),
        'Databases': set(),
        'Technologies': set(),
        'Domain Knowledge': set()
    }
    
    for project in projects:
        all_skills['Programming'].update(project.skill.programming_languages)
        all_skills['Frameworks'].update(project.skill.frameworks)
        all_skills['Databases'].update(project.skill.databases)
        all_skills['Technologies'].update(project.skill.other_technologies)
        all_skills['Domain Knowledge'].update(project.skill.knowledge_area)
    
    # Create DataFrame for skills summary
    skills_data = {k: sorted(v) for k, v in all_skills.items() if v}
    if skills_data:
        max_skills = max(len(v) for v in skills_data.values())
        skills_data = {k: v + [''] * (max_skills - len(v)) for k, v in skills_data.items()}
        df = pd.DataFrame(skills_data)
        
        # Display skills table with custom styling
        styled_df = (
            df.style
            .hide(axis="index")
            .format(lambda x: '' if pd.isna(x) else x)
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('text-align', 'left'),
                    ('font-size', '14px'),
                    ('padding', '5px'),
                    ('background-color', '#f0f2f6')
                ]},
                {'selector': 'td', 'props': [
                    ('text-align', 'left'),
                    ('font-size', '14px'),
                    ('padding', '5px')
                ]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No skills found in the projects.")

def display_technical_skills(skills):
    """Display overall technical skills."""
    st.markdown("### Technical Skills")
    
    # Create skills dataframe
    skills_data = {
        'Programming': skills.programming_languages,
        'Frameworks': skills.frameworks,
        'Databases': skills.databases,
        'Other Technologies': skills.other_technologies,
        'Knowledge Areas': skills.knowledge_area
    }
    
    # Filter out empty categories
    skills_data = {k: v for k, v in skills_data.items() if v}
    
    if skills_data:
        max_skills = max(len(v) for v in skills_data.values())
        skills_data = {k: v + [''] * (max_skills - len(v)) for k, v in skills_data.items()}
        df = pd.DataFrame(skills_data)
        
        styled_df = (
            df.style
            .hide(axis="index")
            .format(lambda x: '' if pd.isna(x) else x)
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('text-align', 'left'),
                    ('font-size', '14px'),
                    ('padding', '5px'),
                    ('background-color', '#f0f2f6')
                ]},
                {'selector': 'td', 'props': [
                    ('text-align', 'left'),
                    ('font-size', '14px'),
                    ('padding', '5px')
                ]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No technical skills found.")

def display_extra_curricular(extra):
    """Display extra-curricular activities."""
    st.markdown("### Extra-Curricular Activities")
    
    # Create activities dataframe
    activities_data = {
        'Leadership': extra.leadership,
        'Awards': extra.awards,
        'Certifications': extra.certifications,
        'Activities': extra.activities,
        'Languages': extra.languages
    }
    
    # Filter out empty categories
    activities_data = {k: v for k, v in activities_data.items() if v}
    
    if activities_data:
        max_items = max(len(v) for v in activities_data.values())
        activities_data = {k: v + [''] * (max_items - len(v)) for k, v in activities_data.items()}
        df = pd.DataFrame(activities_data)
        
        styled_df = (
            df.style
            .hide(axis="index")
            .format(lambda x: '' if pd.isna(x) else x)
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('text-align', 'left'),
                    ('font-size', '14px'),
                    ('padding', '5px'),
                    ('background-color', '#f0f2f6')
                ]},
                {'selector': 'td', 'props': [
                    ('text-align', 'left'),
                    ('font-size', '14px'),
                    ('padding', '5px')
                ]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No extra-curricular activities found.")

def main():
    """Main Streamlit application."""
    st.title("📄 Resume Parser")
    
    # Sidebar
    st.sidebar.title("Upload Resume")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file:
        with st.spinner("Parsing resume..."):
            file_content = uploaded_file.read()
            parsed_data = parse_resume_to_dict(file_content, uploaded_file.name)
            
            if parsed_data:
                resume, extra = reconstruct_resume_info(parsed_data)
                
                # Save data to files using utility function
                output_dir = Path("data")
                file_paths = save_resume_data(resume, extra, output_dir)
                
                # Display token usage
                display_token_usage(parsed_data['tokens'])
                
                # Display parsed information
                st.success("Resume parsed successfully!")
                
                # Download buttons
                st.sidebar.markdown("### Download Parsed Data")
                for data_type, file_path in file_paths.items():
                    with open(file_path, 'r') as f:
                        csv_data = f.read()
                    st.sidebar.download_button(
                        label=f"Download {data_type.title()} CSV",
                        data=csv_data,
                        file_name=f"{resume.metadata.reg_no}_{data_type}.csv",
                        mime="text/csv"
                    )
                
                # Add download button for raw LLM response
                raw_response_path = Path("data") / "raw_responses" / resume.metadata.reg_no / "llm_response.json"
                if raw_response_path.exists():
                    with open(raw_response_path, 'r') as f:
                        json_data = f.read()
                    st.sidebar.download_button(
                        label="Download Raw LLM Response",
                        data=json_data,
                        file_name=f"{resume.metadata.reg_no}_llm_response.json",
                        mime="application/json"
                    )
                
                # Display sections
                display_metadata(resume.metadata, parsed_data['tokens']['scores'])
                st.markdown("---")
                
                display_academic_performance(resume.academic_performance)
                st.markdown("---")
                
                display_technical_skills(resume.technical_skills)
                st.markdown("---")
                
                display_projects(resume.projects)
                st.markdown("---")
                
                display_extra_curricular(extra)
    else:
        st.info("👈 Upload a resume PDF to get started!")

if __name__ == "__main__":
    main() 