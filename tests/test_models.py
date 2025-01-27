import pytest
from pydantic import ValidationError

from resume_parser.models import (
    StudentMetadata,
    AcademicDegreePerformance,
    TechnicalSkills,
    Projects,
    ResumeInfo
)

def test_student_metadata_validation():
    """Test StudentMetadata model validation."""
    # Test valid data
    valid_data = {
        "name": "Test Student",
        "gender": "Male",
        "reg_no": "TEST001",
        "dob": "1990-01-01",
        "email": "test@example.com",
        "phone": "1234567890",
        "mobile": "0987654321",
        "branch": "Computer Science",
        "degree": "B.Tech"
    }
    metadata = StudentMetadata(**valid_data)
    assert metadata.name == "Test Student"
    
    # Test invalid data
    invalid_data = valid_data.copy()
    invalid_data.pop("name")
    with pytest.raises(ValidationError):
        StudentMetadata(**invalid_data)

def test_academic_performance_validation():
    """Test AcademicDegreePerformance model validation."""
    valid_data = {
        "semester": 1,
        "duration": "Dec 2020",
        "sgpa": 9.0,
        "cgpa": 9.0,
        "degree": "B.Tech"
    }
    performance = AcademicDegreePerformance(**valid_data)
    assert performance.sgpa == 9.0
    
    # Test invalid SGPA
    invalid_data = valid_data.copy()
    invalid_data["sgpa"] = 11.0  # Invalid SGPA
    with pytest.raises(ValidationError):
        AcademicDegreePerformance(**invalid_data)

def test_technical_skills_validation():
    """Test TechnicalSkills model validation."""
    valid_data = {
        "programming_languages": ["Python", "Java"],
        "frameworks": ["Django"],
        "databases": ["PostgreSQL"],
        "other_technologies": ["Git"],
        "knowledge_area": ["Web Development"]
    }
    skills = TechnicalSkills(**valid_data)
    assert "Python" in skills.programming_languages
    
    # Test with empty lists
    empty_data = {
        "programming_languages": [],
        "frameworks": [],
        "databases": [],
        "other_technologies": [],
        "knowledge_area": []
    }
    skills = TechnicalSkills(**empty_data)
    assert len(skills.programming_languages) == 0 