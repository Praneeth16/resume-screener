import pytest
from unittest.mock import patch, Mock

from resume_parser.main import process_resumes

@pytest.fixture
def mock_splitter(monkeypatch):
    """Mock ResumeSplitter class."""
    mock = Mock()
    mock.return_value.split_resumes.return_value = 3
    mock.return_value.verify_split.return_value = True
    monkeypatch.setattr("resume_parser.main.ResumeSplitter", mock)
    return mock

@pytest.fixture
def mock_parser(monkeypatch):
    """Mock ResumeParser class."""
    mock = Mock()
    mock.return_value.parse_resume.return_value = Mock()
    monkeypatch.setattr("resume_parser.main.ResumeParser", mock)
    return mock

def test_process_resumes(mock_splitter, mock_parser, tmp_path):
    """Test the main resume processing function."""
    input_pdf = tmp_path / "test.pdf"
    output_dir = tmp_path / "output"
    
    # Create test files
    input_pdf.touch()
    output_dir.mkdir()
    (output_dir / "test1.pdf").touch()
    (output_dir / "test2.pdf").touch()
    
    # Run process_resumes
    process_resumes(str(input_pdf), str(output_dir))
    
    # Verify calls
    mock_splitter.return_value.split_resumes.assert_called_once()
    mock_splitter.return_value.verify_split.assert_called_once()
    assert mock_parser.return_value.parse_resume.call_count == 2

def test_process_resumes_split_verification_failed(mock_splitter, mock_parser, tmp_path):
    """Test handling of split verification failure."""
    mock_splitter.return_value.verify_split.return_value = False
    
    with pytest.raises(ValueError, match="Resume splitting verification failed"):
        process_resumes(str(tmp_path / "test.pdf"), str(tmp_path / "output")) 