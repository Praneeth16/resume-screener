import os
import asyncio
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from .document_splitter import ResumeSplitter
from .parser import ResumeParser
from .utils import TokenUsage, save_resume_data

async def process_resume(parser: ResumeParser, resume_path: Path, csv_output_dir: Path):
    """Process a single resume asynchronously."""
    try:
        resume_info, extra_info, token_usage = await parser.parse_resume(str(resume_path))
        
        # Save resume information using utility function
        save_resume_data(resume_info, extra_info, csv_output_dir)
        
        # Save token usage
        token_usage.save_to_csv(csv_output_dir)
        
        print(f"Successfully parsed and saved resume: {resume_path.name}")
        return True
    except Exception as e:
        print(f"Error processing resume {resume_path.name}: {str(e)}")
        return False

async def process_resumes_async(input_pdf: str, output_dir: str) -> None:
    """Process resumes asynchronously."""
    # Load environment variables
    load_dotenv()
    
    # Create output directories
    pdf_output_dir = Path(output_dir) / "pdfs"
    csv_output_dir = Path(output_dir) / "parsed_data"
    os.makedirs(pdf_output_dir, exist_ok=True)
    os.makedirs(csv_output_dir, exist_ok=True)
    
    # Split the combined PDF
    splitter = ResumeSplitter(input_pdf, pdf_output_dir)
    num_resumes = splitter.split_resumes()
    
    if not splitter.verify_split():
        raise ValueError("Resume splitting verification failed")
        
    print(f"Successfully split {num_resumes} resumes")
    
    # Initialize parser
    parser = ResumeParser(
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        base_url=os.getenv('DEEPSEEK_URL')
    )
    
    # Process resumes concurrently
    tasks = []
    for resume_file in pdf_output_dir.glob("*.pdf"):
        task = process_resume(parser, resume_file, csv_output_dir)
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Print summary
    successful = sum(results)
    print(f"\nProcessing complete:")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {len(results) - successful}")

def process_resumes(input_pdf: str, output_dir: str) -> None:
    """Entry point for resume processing."""
    asyncio.run(process_resumes_async(input_pdf, output_dir))

if __name__ == "__main__":
    process_resumes(
        input_pdf='data/resumes_compiled.pdf',
        output_dir='data/output'
    ) 