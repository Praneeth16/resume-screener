import os
import pytest
from pypdf import PdfWriter, PdfReader
from pathlib import Path

from resume_parser.document_splitter import ResumeSplitter

@pytest.fixture
def combined_pdf(test_data_dir, sample_pdfs):
    """Create a combined PDF from sample PDFs."""
    output_path = test_data_dir / "combined_resumes.pdf"
    writer = PdfWriter()
    
    # Combine the sample PDFs
    for pdf_path in sample_pdfs:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)
    
    # Save the combined PDF
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    return output_path

def test_resume_splitter_initialization(combined_pdf, output_dir):
    """Test ResumeSplitter initialization."""
    splitter = ResumeSplitter(combined_pdf, output_dir)
    assert splitter.input_file == combined_pdf
    assert splitter.output_dir == output_dir
    assert "NATIONAL INSTITUTE OF TECHNOLOGY KARNATAKA" in splitter.pattern

def test_split_resumes(combined_pdf, output_dir, sample_pdfs):
    """Test splitting resumes into individual files."""
    os.makedirs(output_dir, exist_ok=True)
    splitter = ResumeSplitter(combined_pdf, output_dir)
    
    num_resumes = splitter.split_resumes()
    assert num_resumes == len(sample_pdfs)  # Expected number of resumes
    
    # Check if files were created
    pdf_files = list(output_dir.glob("*.pdf"))
    assert len(pdf_files) == len(sample_pdfs)
    
    # Check if original filenames are preserved
    original_names = {pdf.name for pdf in sample_pdfs}
    output_names = {pdf.name for pdf in pdf_files}
    assert output_names == original_names

def test_verify_split(combined_pdf, output_dir):
    """Test verification of split operation."""
    splitter = ResumeSplitter(combined_pdf, output_dir)
    splitter.split_resumes()
    
    assert splitter.verify_split() is True

def test_extract_filename():
    """Test extraction of filename from text."""
    splitter = ResumeSplitter("dummy.pdf", "dummy_dir")
    
    # Test with registration number
    text = "Some text\nReg. No. : 19CO123\nMore text"
    assert splitter._extract_filename(text, 0) == "19CO123.pdf"
    
    # Test without registration number
    text = "Some text without registration number"
    assert splitter._extract_filename(text, 5) == "page_5.pdf"

def test_split_resumes_with_empty_pdf(output_dir):
    """Test splitting with an empty PDF."""
    # Create an empty PDF
    empty_pdf = output_dir / "empty.pdf"
    writer = PdfWriter()
    with open(empty_pdf, 'wb') as f:
        writer.write(f)
    
    splitter = ResumeSplitter(empty_pdf, output_dir)
    num_resumes = splitter.split_resumes()
    assert num_resumes == 0

def test_split_resumes_with_invalid_pdf(output_dir):
    """Test splitting with an invalid PDF."""
    # Create an invalid PDF file
    invalid_pdf = output_dir / "invalid.pdf"
    with open(invalid_pdf, 'w') as f:
        f.write("This is not a PDF file")
    
    splitter = ResumeSplitter(invalid_pdf, output_dir)
    with pytest.raises(Exception):
        splitter.split_resumes() 