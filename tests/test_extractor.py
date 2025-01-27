import pytest
from resume_parser.extractor import ExtraCurricularExtractor
from PyPDF2 import PdfReader

def test_extractor_initialization(extractor):
    """Test extractor initialization."""
    assert isinstance(extractor, ExtraCurricularExtractor)

def test_pattern_matching(extractor):
    """Test pattern matching functionality."""
    test_text = """
    LEADERSHIP:
    - Team Lead for College Tech Club
    - Project Coordinator for Hackathon
    
    AWARDS AND ACHIEVEMENTS:
    - First Prize in Coding Competition
    - Best Project Award
    
    CERTIFICATIONS:
    - AWS Certified Developer
    - Google Cloud Professional
    
    ACTIVITIES:
    - Member of College Sports Team
    - Volunteer at NGO
    """
    
    result = extractor.extract(test_text)
    assert isinstance(result.leadership, list)
    assert isinstance(result.awards, list)
    assert isinstance(result.certifications, list)
    assert isinstance(result.activities, list)
    
    assert len(result.leadership) > 0
    assert len(result.awards) > 0
    assert len(result.certifications) > 0
    assert len(result.activities) > 0

def test_reference_exclusion(extractor):
    """Test that references are excluded from extraction."""
    test_text = """
    LEADERSHIP:
    - Team Lead
    
    REFERENCE 1:
    Mr. John Doe
    Professor, Computer Science
    
    REFERENCE 2:
    Ms. Jane Smith
    Senior Developer
    """
    
    result = extractor.extract(test_text)
    assert len(result.leadership) == 1
    assert "REFERENCE" not in ' '.join(result.leadership)

def test_real_pdf_extraction(extractor, test_pdf_path):
    """Test extraction from a real PDF file."""
    reader = PdfReader(test_pdf_path)
    text = "\n".join([page.extract_text() for page in reader.pages])
    
    result = extractor.extract(text)
    
    # Basic validation
    assert isinstance(result.leadership, list)
    assert isinstance(result.awards, list)
    assert isinstance(result.certifications, list)
    assert isinstance(result.activities, list)
    
    # Content validation
    all_items = (
        result.leadership +
        result.awards +
        result.certifications +
        result.activities
    )
    assert len(all_items) > 0, "Should extract at least some items"
    
    # Check for data quality
    for item in all_items:
        assert len(item.strip()) > 0, "Items should not be empty"
        assert len(item.split()) >= 2, "Items should have at least 2 words"

def test_text_cleaning(extractor):
    """Test text cleaning functionality."""
    test_text = """
    LEADERSHIP:
    • Team Lead (with bullet)
    * Project Lead (with asterisk)
    - Technical Lead (with hyphen)
    1. First Lead (with number)
    """
    
    result = extractor.extract(test_text)
    assert len(result.leadership) == 4
    
    for item in result.leadership:
        assert not item.startswith('•')
        assert not item.startswith('*')
        assert not item.startswith('-')
        assert not item.startswith('1.') 