from dataclasses import dataclass
from typing import Optional, Dict, List
import csv
import os
import numpy as np
import pandas as pd
from pathlib import Path

from .models import ResumeInfo, ExtraCurricular

__all__ = ['TokenUsage', 'save_resume_data', 'calculate_candidate_score']

@dataclass
class TokenUsage:
    """Track token usage for API calls."""
    reg_no: str
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    cached_tokens: int
    audio_tokens: int
    reasoning_tokens: int
    
    @classmethod
    def from_completion_usage(cls, reg_no: str, usage):
        """Create TokenUsage from OpenAI completion usage."""
        return cls(
            reg_no=reg_no,
            completion_tokens=usage.completion_tokens,
            prompt_tokens=usage.prompt_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=usage.prompt_tokens_details.cached_tokens,
            audio_tokens=0,   # Not applicable
            reasoning_tokens=0  # Not applicable
        )

def calculate_academic_score(academic_performance: List[dict]) -> float:
    """Calculate academic score (20% of total)."""
    if not academic_performance:
        return 0.0
    
    # Extract CGPAs
    cgpas = [float(perf['cgpa']) for perf in academic_performance]
    sgpas = [float(perf['sgpa']) for perf in academic_performance]
    
    # Calculate components
    avg_cgpa = np.mean(cgpas)
    std_dev = np.std(sgpas) if len(sgpas) > 1 else 0
    
    # Calculate score using formula
    score = (avg_cgpa * 0.75) + ((10 - std_dev) * 0.25)
    
    # Normalize to 20%
    return min(score * 2, 20.0)  # Multiply by 2 to scale to 20%

def count_mapper(num_skills: int) -> int:
    """Map number of skills to points."""
    if num_skills == 0:
        return 0
    elif num_skills <=3:
        return 1
    else:
        return 2

def calculate_technical_score(technical_skills: dict) -> float:
    """Calculate technical skills score (35% of total)."""
    # Calculate raw points
    points = (
        count_mapper(len(technical_skills['programming_languages'])) +
        count_mapper(len(technical_skills['frameworks'])) +
        count_mapper(len(technical_skills['databases'])) +
        count_mapper(len(technical_skills['other_technologies'])) +
        count_mapper(len(technical_skills['knowledge_area']))
    )
    
    max_expected_points = 10
    # Normalize to 35%
    normalized_score = (points / max_expected_points) * 35
    
    return min(normalized_score, 35.0)

def calculate_projects_score(projects: List[dict]) -> float:
    """Calculate projects score (30% of total)."""
    total_points = 0
    
    for project in projects:
        # Base points for project
        points = 5
        
        # Additional points for internships
        if project['company'].lower() not in ['personal', 'na', 'n/a']:
            points += 5  # Additional points for internship
        
        # Points for technical relevance based on skills used
        skill_points = count_mapper(
            len(project['skill']['programming_languages']) +
            len(project['skill']['frameworks']) +
            len(project['skill']['databases']) +
            len(project['skill']['knowledge_area'])
        )
        relevance_points = min(skill_points*2, 10)  # Cap at 5 points
        
        total_points += points + relevance_points
    
    # Normalize to 30%
    max_expected_points = 100  # Adjust this
    normalized_score = (total_points / max_expected_points) * 30
    
    return min(normalized_score, 30.0)

def calculate_extracurricular_score(extra_curricular: dict) -> float:
    """Calculate extracurricular score (15% of total)."""
    # Calculate raw points using formula
    points = count_mapper(
        len(extra_curricular['leadership']) +
        len(extra_curricular['awards']) +
        len(extra_curricular['certifications']) +
        len(extra_curricular['activities'])
    )
    
    # Normalize to 15%
    max_expected_points = 8  # Adjust this
    normalized_score = (points / max_expected_points) * 15
    
    return min(normalized_score, 15.0)

def calculate_candidate_score(resume_info: ResumeInfo, extra_info: ExtraCurricular) -> Dict[str, float]:
    """Calculate overall candidate score and component scores."""
    
    # Convert to dictionaries for easier handling
    academic_data = [p.model_dump() for p in resume_info.academic_performance]
    technical_data = resume_info.technical_skills.model_dump()
    projects_data = [p.model_dump() for p in resume_info.projects]
    extra_data = extra_info.model_dump()
    
    # Calculate component scores
    academic_score = calculate_academic_score(academic_data)
    technical_score = calculate_technical_score(technical_data)
    projects_score = calculate_projects_score(projects_data)
    extra_score = calculate_extracurricular_score(extra_data)
    
    # Calculate total score
    total_score = academic_score + technical_score + projects_score + extra_score
    
    return {
        'total_score': round(total_score, 2),
        'academic_score': round(academic_score, 2),
        'technical_score': round(technical_score, 2),
        'projects_score': round(projects_score, 2),
        'extra_score': round(extra_score, 2)
    }

def save_resume_data(resume_info: ResumeInfo, extra_info: ExtraCurricular, output_dir: Path) -> Dict[str, str]:
    """Save resume data to CSV files and return file paths."""
    reg_no = resume_info.metadata.reg_no
    base_dir = output_dir / "parsed_data" / reg_no
    os.makedirs(base_dir, exist_ok=True)
    
    file_paths = {}
    
    # Calculate scores
    scores = calculate_candidate_score(resume_info, extra_info)
    
    # Save metadata with scores
    metadata_file = base_dir / f"{reg_no}_metadata.csv"
    metadata_dict = resume_info.metadata.model_dump()
    metadata_dict.update(scores)  # Add scores to metadata
    pd.DataFrame([metadata_dict]).to_csv(metadata_file, index=False)
    file_paths['metadata'] = str(metadata_file)
    
    # Save academic performance
    academic_file = base_dir / f"{reg_no}_academic.csv"
    academic_data = [{
        'semester': p.semester,
        'duration': p.duration,
        'sgpa': p.sgpa,
        'cgpa': p.cgpa,
        'degree': p.degree
    } for p in resume_info.academic_performance]
    pd.DataFrame(academic_data).to_csv(academic_file, index=False)
    file_paths['academic'] = str(academic_file)
    
    # Save technical skills
    skills_file = base_dir / f"{reg_no}_skills.csv"
    skills_dict = resume_info.technical_skills.model_dump()
    skills_data = {k: ';'.join(v) for k, v in skills_dict.items()}
    pd.DataFrame([skills_data]).to_csv(skills_file, index=False)
    file_paths['skills'] = str(skills_file)
    
    # Save extra curricular
    extra_file = base_dir / f"{reg_no}_extracurricular.csv"
    extra_dict = extra_info.model_dump()
    extra_data = {k: ';'.join(v) for k, v in extra_dict.items()}
    pd.DataFrame([extra_data]).to_csv(extra_file, index=False)
    file_paths['extracurricular'] = str(extra_file)
    
    # Save projects
    projects_file = base_dir / f"{reg_no}_projects.csv"
    project_data = [{
        'name': p.name,
        'company': p.company,
        'duration': p.duration,
        'programming_languages': ';'.join(p.skill.programming_languages),
        'frameworks': ';'.join(p.skill.frameworks),
        'databases': ';'.join(p.skill.databases),
        'other_technologies': ';'.join(p.skill.other_technologies),
        'knowledge_area': ';'.join(p.skill.knowledge_area)
    } for p in resume_info.projects]
    pd.DataFrame(project_data).to_csv(projects_file, index=False)
    file_paths['projects'] = str(projects_file)
    
    return file_paths
