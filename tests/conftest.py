import os
import random
import pytest
from pathlib import Path
from shutil import copy2
from resume_parser.models import ResumeInfo, ExtraCurricular
from resume_parser.parser import ResumeParser
from resume_parser.extractor import ExtraCurricularExtractor

@pytest.fixture
def test_data_dir():
    """Fixture to provide test data directory path."""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def sample_pdfs(test_data_dir):
    """Fixture to provide sample PDFs from candidate_resume folder."""
    # Path to the actual resume PDFs
    source_dir = Path(__file__).parent.parent / "data" / "candidate_resume"
    
    # Create test_data directory if it doesn't exist
    os.makedirs(test_data_dir, exist_ok=True)
    
    # Get all PDF files from source directory
    pdf_files = list(source_dir.glob("*.pdf"))
    
    # Randomly select 3 PDFs
    selected_pdfs = random.sample(pdf_files, 3)
    
    # Copy selected PDFs to test_data directory
    copied_paths = []
    for pdf in selected_pdfs:
        dest_path = test_data_dir / pdf.name
        copy2(pdf, dest_path)
        copied_paths.append(dest_path)
    
    return copied_paths

@pytest.fixture
def output_dir(tmp_path):
    """Fixture to provide a temporary directory for output files."""
    return tmp_path / "output"

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up mock environment variables."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
    monkeypatch.setenv("DEEPSEEK_URL", "https://test.api.deepseek.com")

@pytest.fixture
def test_pdf_path():
    """Fixture to provide test PDF path."""
    return Path("data/candidate_resume/06IT68.pdf")

@pytest.fixture
def output_dir():
    """Fixture to provide test output directory."""
    path = Path("data/test_output")
    path.mkdir(parents=True, exist_ok=True)
    return path

@pytest.fixture
def parser():
    """Fixture to provide ResumeParser instance."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_URL")
    return ResumeParser(api_key=api_key, base_url=base_url)

@pytest.fixture
def extractor():
    """Fixture to provide ExtraCurricularExtractor instance."""
    return ExtraCurricularExtractor()

@pytest.fixture
def sample_resume_info():
    """Fixture to provide sample ResumeInfo for testing."""
    return ResumeInfo(
        metadata={
            "name": "Test Student",
            "reg_no": "06IT68",
            "email": "test@example.com",
            "phone": "1234567890"
        },
        academic_performance=[{
            "semester": 1,
            "duration": "2021-22",
            "sgpa": "9.0",
            "cgpa": "9.0",
            "degree": "B.Tech"
        }],
        technical_skills={
            "programming_languages": ["Python", "Java"],
            "frameworks": ["Django", "Spring"],
            "databases": ["MySQL"],
            "other_technologies": ["Git"],
            "knowledge_area": ["Machine Learning"]
        },
        projects=[{
            "name": "Test Project",
            "company": "Personal",
            "duration": "3 months",
            "skill": {
                "programming_languages": ["Python"],
                "frameworks": ["Django"],
                "databases": ["MySQL"],
                "other_technologies": ["Git"],
                "knowledge_area": ["Web Development"]
            }
        }]
    )

@pytest.fixture
def sample_extra_info():
    """Fixture to provide sample ExtraCurricular for testing."""
    return ExtraCurricular(
        leadership=["Team Lead - College Club"],
        awards=["Best Project Award"],
        certifications=["AWS Certified"],
        activities=["Volunteer Work"],
        languages=["English", "Hindi"]
    ) 