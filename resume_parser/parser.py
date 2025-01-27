import os
import re
import json
import asyncio
from typing import Tuple
from pathlib import Path

import instructor
from openai import OpenAI
from pypdf import PdfReader

from .models import ResumeInfo, ExtraCurricular
from .utils import TokenUsage
from .extractor import ExtraCurricularExtractor

class ResumeParser:
    def __init__(self, api_key: str, base_url: str):
        """Initialize ResumeParser with API credentials.
        
        Args:
            api_key: API key for the LLM service
            base_url: Base URL for the LLM service
        """
        self.client = instructor.from_openai(OpenAI(api_key=api_key, base_url=base_url))
        self.extractor = ExtraCurricularExtractor()
    
    async def _extract_resume_info(self, text: str) -> Tuple[ResumeInfo, object]:
        """Extract main resume information."""
        response, completion = await asyncio.to_thread(
            self.client.chat.completions.create_with_completion,
            model="deepseek-chat",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert resume parsing system. Extract the exact information mentioned in resumes into a structured JSON format. If any information is missing return NA. The output should match this structure exactly:\n\n{metadata: {name, gender, reg_no, dob, email, phone, mobile, branch, degree}, academic_performance: [{semester, duration, sgpa, cgpa, degree}], projects: [{name, company, duration, skill: {programming_languages: [], frameworks: [], databases: [], other_technologies: [], knowledge_area: []}}], technical_skills: {programming_languages: [], frameworks: [], databases: [], other_technologies: [], knowledge_area: []}}"
                },
                {
                    "role": "user", 
                    "content": f"Candidate resume:\n\n{text}"
                },
            ],
            temperature=0.0,
            response_model=ResumeInfo
        )
        
        # Parse the JSON response into ResumeInfo model
        #response_json = json.loads(completion.choices[0].message.content)
        #resume_info = response.model_dump()
        
        return response, completion

    async def parse_resume(self, pdf_path: str) -> Tuple[ResumeInfo, ExtraCurricular, TokenUsage]:
        """Parse a resume PDF and extract structured information.
        
        Args:
            pdf_path: Path to the resume PDF file
            
        Returns:
            Tuple of (ResumeInfo, ExtraCurricular, TokenUsage)
        """
        # Read PDF and extract text
        reader = PdfReader(pdf_path)
        text = "\n".join([
            re.sub(r'\s\s+', ' ', page.extract_text()) 
            for page in reader.pages
        ])

        # Extract main resume info using LLM
        resume_info, completion = await self._extract_resume_info(text)
        print(resume_info)
        print(completion)
        # Extract extra-curricular info using pattern matching
        extra_info = self.extractor.extract(text)
        print('Extra-curricular info:')
        print(extra_info)
        # Create token usage info
        total_usage = TokenUsage.from_completion_usage(
            reg_no=resume_info.metadata.reg_no,
            usage=completion.usage
        )
        
        # Save raw LLM response
        output_dir = Path("data") / "raw_responses" / resume_info.metadata.reg_no
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "llm_response.json", "w") as f:
            json.dump({
                "response": resume_info.model_dump(),
                "usage": {
                    "completion_tokens": completion.usage.completion_tokens,
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "total_tokens": completion.usage.total_tokens
                }
            }, f, indent=2)
        
        return resume_info, extra_info, total_usage 