import pytest
from resume_parser.utils import (
    calculate_academic_score,
    calculate_technical_score,
    calculate_projects_score,
    calculate_extracurricular_score,
    calculate_candidate_score
)

def test_academic_score_calculation():
    """Test academic score calculation."""
    academic_data = [
        {
            "semester": 1,
            "duration": "2021-22",
            "sgpa": "9.0",
            "cgpa": "9.0",
            "degree": "B.Tech"
        },
        {
            "semester": 2,
            "duration": "2021-22",
            "sgpa": "8.5",
            "cgpa": "8.75",
            "degree": "B.Tech"
        }
    ]
    
    score = calculate_academic_score(academic_data)
    assert 0 <= score <= 20, "Academic score should be between 0 and 20"
    assert isinstance(score, float), "Score should be a float"

def test_technical_score_calculation(sample_resume_info):
    """Test technical skills score calculation."""
    technical_data = sample_resume_info.technical_skills.model_dump()
    score = calculate_technical_score(technical_data)
    
    assert 0 <= score <= 35, "Technical score should be between 0 and 35"
    assert isinstance(score, float), "Score should be a float"

def test_projects_score_calculation(sample_resume_info):
    """Test projects score calculation."""
    projects_data = [p.model_dump() for p in sample_resume_info.projects]
    score = calculate_projects_score(projects_data)
    
    assert 0 <= score <= 30, "Projects score should be between 0 and 30"
    assert isinstance(score, float), "Score should be a float"

def test_extracurricular_score_calculation(sample_extra_info):
    """Test extracurricular score calculation."""
    extra_data = sample_extra_info.model_dump()
    score = calculate_extracurricular_score(extra_data)
    
    assert 0 <= score <= 15, "Extracurricular score should be between 0 and 15"
    assert isinstance(score, float), "Score should be a float"

def test_total_score_calculation(sample_resume_info, sample_extra_info):
    """Test total score calculation."""
    scores = calculate_candidate_score(sample_resume_info, sample_extra_info)
    
    assert isinstance(scores, dict), "Should return a dictionary"
    assert "total_score" in scores, "Should include total score"
    assert "academic_score" in scores, "Should include academic score"
    assert "technical_score" in scores, "Should include technical score"
    assert "projects_score" in scores, "Should include projects score"
    assert "extra_score" in scores, "Should include extra score"
    
    total = scores["total_score"]
    assert 0 <= total <= 100, "Total score should be between 0 and 100"
    
    # Verify that component scores add up to total
    component_sum = (
        scores["academic_score"] +
        scores["technical_score"] +
        scores["projects_score"] +
        scores["extra_score"]
    )
    assert abs(total - component_sum) < 0.1, "Component scores should sum to total score" 