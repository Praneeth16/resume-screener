import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from pdfminer.pdfdocument import PdfReader

from resume_parser.parser import ResumeParser
from resume_parser.models import ResumeInfo, StudentMetadata, AcademicDegreePerformance, ExtraCurricular
from resume_parser.utils import save_resume_data

@pytest.fixture
def mock_openai_response():
    """Create a mock response for OpenAI API."""
    return ResumeInfo(
        metadata=StudentMetadata(
            name="Test Student",
            gender="Male",
            reg_no="TEST001",
            dob="1990-01-01",
            email="test@example.com",
            phone="1234567890",
            mobile="0987654321",
            branch="Computer Science",
            degree="B.Tech"
        ),
        academic_performance=[
            AcademicDegreePerformance(
                semester=1,
                duration="Dec 2020",
                sgpa=9.0,
                cgpa=9.0,
                degree="B.Tech"
            )
        ],
        projects=[]
    )

@pytest.fixture
def parser():
    """Create a ResumeParser instance with mock credentials."""
    return ResumeParser("test_api_key", "https://test.api.deepseek.com")

@patch('instructor.from_openai')
def test_parser_initialization(mock_instructor):
    """Test ResumeParser initialization."""
    parser = ResumeParser("test_key", "test_url")
    assert mock_instructor.called

def test_parse_resume_with_real_pdf(parser, mock_openai_response, sample_pdfs):
    """Test resume parsing functionality with a real PDF."""
    # Use the first sample PDF
    test_pdf = sample_pdfs[0]
    
    # Mock OpenAI client response
    mock_client = Mock()
    mock_client.chat.completions.create_with_completion.return_value = (
        mock_openai_response,
        Mock()
    )
    parser.client = mock_client
    
    # Test parsing
    result = parser.parse_resume(test_pdf)
    
    assert isinstance(result, ResumeInfo)
    assert result.metadata.name == "Test Student"
    assert result.metadata.reg_no == "TEST001"
    assert len(result.academic_performance) == 1
    assert result.academic_performance[0].sgpa == 9.0

def test_parser_initialization(parser):
    """Test parser initialization."""
    assert isinstance(parser, ResumeParser)
    assert parser.api_key is not None
    assert parser.base_url is not None

@pytest.mark.asyncio
async def test_resume_parsing(parser, test_pdf_path):
    """Test complete resume parsing pipeline."""
    # Parse resume
    resume_info = await parser.parse_resume(test_pdf_path)
    
    # Validate basic structure
    assert isinstance(resume_info, ResumeInfo)
    assert resume_info.metadata is not None
    assert resume_info.academic_performance is not None
    assert resume_info.technical_skills is not None
    assert resume_info.projects is not None
    
    # Validate metadata
    assert resume_info.metadata.reg_no == "06IT68"
    assert resume_info.metadata.name is not None
    assert resume_info.metadata.email is not None
    
    # Validate academic performance
    assert len(resume_info.academic_performance) > 0
    for performance in resume_info.academic_performance:
        assert performance.semester is not None
        assert performance.sgpa is not None
        assert performance.cgpa is not None
    
    # Validate technical skills
    skills = resume_info.technical_skills
    assert len(skills.programming_languages) > 0
    assert len(skills.frameworks) >= 0
    assert len(skills.databases) >= 0
    
    # Validate projects
    assert len(resume_info.projects) > 0
    for project in resume_info.projects:
        assert project.name is not None
        assert project.duration is not None
        assert project.skill is not None

@pytest.mark.asyncio
async def test_complete_pipeline(parser, extractor, test_pdf_path, output_dir):
    """Test the complete pipeline including parsing, extraction, and saving."""
    # Parse resume
    resume_info = await parser.parse_resume(test_pdf_path)
    
    # Extract extra-curricular activities
    with open(test_pdf_path, 'rb') as pdf_file:
        text = "\n".join([page.extract_text() for page in PdfReader(pdf_file).pages])
    extra_info = extractor.extract(text)
    
    assert isinstance(extra_info, ExtraCurricular)
    
    # Save data
    file_paths = save_resume_data(resume_info, extra_info, output_dir)
    
    # Validate saved files
    assert isinstance(file_paths, dict)
    assert all(Path(path).exists() for path in file_paths.values())
    
    # Validate file contents
    metadata_path = file_paths['metadata']
    academic_path = file_paths['academic']
    skills_path = file_paths['skills']
    projects_path = file_paths['projects']
    extra_path = file_paths['extracurricular']
    
    assert Path(metadata_path).stat().st_size > 0
    assert Path(academic_path).stat().st_size > 0
    assert Path(skills_path).stat().st_size > 0
    assert Path(projects_path).stat().st_size > 0
    assert Path(extra_path).stat().st_size > 0

def test_error_handling(parser):
    """Test error handling in parser."""
    with pytest.raises(FileNotFoundError):
        await parser.parse_resume(Path("nonexistent.pdf"))
    
    with pytest.raises(ValueError):
        await parser.parse_resume(Path("tests/test_parser.py"))  # Not a PDF file 