from glob import glob
import os
import re
from typing import List, Optional

from pypdf import PdfReader, PdfWriter


class ResumeSplitter:
    def __init__(self, input_file: str, output_dir: str):
        """Initialize ResumeSplitter with input PDF and output directory.
        
        Args:
            input_file: Path to the combined PDF file containing multiple resumes
            output_dir: Directory where individual resumes will be saved
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.pattern = "NATIONAL INSTITUTE OF TECHNOLOGY KARNATAKA, SURATHKAL P.O SRINIVASNAGAR, MANGALORE-575025"
        
    def split_resumes(self) -> int:
        """Split the combined PDF into individual resume files.
        
        Returns:
            Number of resumes extracted
        """
        reader = PdfReader(self.input_file)
        pages = []
        filename = None
        
        for num in range(len(reader.pages)):
            page = reader.pages[num]
            text = page.extract_text()
            clean_text = re.sub(r'\s\s+', ' ', text).strip()

            # Save the previous resume
            if self.pattern in clean_text:
                if pages:
                    self._save_resume(pages, filename)
                
                # Start the new resume
                pages = [page]
                filename = self._extract_filename(clean_text, num)
            else:
                pages.append(page)
                
        # Save the last resume
        if pages and filename:
            self._save_resume(pages, filename)
            
        return len(glob(os.path.join(self.output_dir, "*.pdf")))
    
    def _save_resume(self, pages: List, filename: str):
        """Save the accumulated pages as a single resume PDF."""
        writer = PdfWriter()
        for page in pages:
            writer.add_page(page)
        
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'wb') as out:
            writer.write(out)
    
    def _extract_filename(self, text: str, page_num: int) -> str:
        """Extract registration number for filename from text."""
        reg_no_line = [line for line in text.split("\n") if 'Reg. No. :' in line]
        if reg_no_line:
            reg_no = reg_no_line[0].split(":")[-1].strip()
        else:
            reg_no = f'page_{page_num}'
        return f"{reg_no}.pdf"
    
    def verify_split(self) -> bool:
        """Verify that all resumes were correctly split.
        
        Returns:
            True if verification passes, False otherwise
        """
        reader = PdfReader(self.input_file)
        clean_texts = "\n".join([re.sub(r'\s\s+', ' ', page.extract_text()) 
                               for page in reader.pages])
        
        pattern_count = len(re.findall(self.pattern, clean_texts))
        file_count = len(glob(os.path.join(self.output_dir, "*.pdf")))
        
        return pattern_count == file_count 