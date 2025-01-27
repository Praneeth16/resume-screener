import re
from typing import List, Dict
from .models import ExtraCurricular

class ExtraCurricularExtractor:
    """Extract extra-curricular activities using pattern matching."""
    
    # Common section headers
    LEADERSHIP_PATTERNS = [
        r"positions?\s+of\s+responsibility",
        r"leadership",
        r"(?:campus|college|university)\s+involvement",
        r"student\s+activities"
    ]
    
    AWARDS_PATTERNS = [
        r"achievements",
        r"awards",
        r"honors",
        r"recognitions?",
        r"scholarships?"
    ]
    
    CERTIFICATION_PATTERNS = [
        r"certifications?",
        r"courses?\s+completed",
        r"training\s+programs?"
    ]
    
    ACTIVITIES_PATTERNS = [
        r"extra.?curricular",
        r"co.?curricular",
        r"sports",
        r"cultural\s+activities?",
        r"volunteer(?:ing)?",
        r"nss|ncc",
        r"competitions?",
        r"clubs?\s+and\s+societies?"
    ]
    
    LANGUAGES_PATTERNS = [
        r"languages?\s+known",
        r"language\s+proficiency",
        r"linguistic"
    ]
    
    # Pattern to identify references
    REFERENCE_PATTERN = re.compile(r"^reference\s*\d*\s*:", re.IGNORECASE)
    
    def __init__(self):
        # Compile all patterns
        self.section_patterns = {
            'leadership': [re.compile(p, re.IGNORECASE) for p in self.LEADERSHIP_PATTERNS],
            'awards': [re.compile(p, re.IGNORECASE) for p in self.AWARDS_PATTERNS],
            'certifications': [re.compile(p, re.IGNORECASE) for p in self.CERTIFICATION_PATTERNS],
            'activities': [re.compile(p, re.IGNORECASE) for p in self.ACTIVITIES_PATTERNS],
            'languages': [re.compile(p, re.IGNORECASE) for p in self.LANGUAGES_PATTERNS]
        }
    
    def _find_section_bounds(self, text: str, patterns: List[re.Pattern]) -> List[tuple]:
        """Find the start and end positions of sections matching the patterns."""
        bounds = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Skip if this is a reference line
            if self.REFERENCE_PATTERN.search(line):
                continue
                
            for pattern in patterns:
                if pattern.search(line):
                    start = i
                    # Look for the next section header or end of text
                    end = len(lines)
                    for j in range(i + 1, len(lines)):
                        # Stop if we hit a reference section
                        if self.REFERENCE_PATTERN.search(lines[j]):
                            end = j
                            break
                        # Stop if we hit another section header
                        for pat_list in self.section_patterns.values():
                            for p in pat_list:
                                if p.search(lines[j]):
                                    end = j
                                    break
                            if end != len(lines):
                                break
                        if end != len(lines):
                            break
                    
                    if start + 1 < end:  # Only include if there's content
                        bounds.append((start + 1, end))
                    break
        
        return bounds
    
    def _extract_items(self, lines: List[str]) -> List[str]:
        """Extract individual items from lines of text."""
        items = []
        current_item = []
        
        for line in lines:
            line = line.strip()
            # Skip reference lines
            if self.REFERENCE_PATTERN.search(line):
                continue
                
            if not line:
                if current_item:
                    items.append(' '.join(current_item))
                    current_item = []
                continue
            
            # Split by full stop if it's a long line
            if len(line) > 50 and '.' in line:
                sentences = [s.strip() for s in line.split('.') if s.strip()]
                for sentence in sentences:
                    if len(sentence.split()) > 3:  # Only include if more than 3 words
                        items.append(sentence)
            else:
                current_item.append(line)
        
        # Add any remaining item
        if current_item:
            items.append(' '.join(current_item))
        
        return items
    
    def _clean_items(self, items: List[str]) -> List[str]:
        """Clean and filter extracted items."""
        cleaned = []
        for item in items:
            # Skip reference items
            if self.REFERENCE_PATTERN.search(item):
                continue
                
            # Remove any numbers or special characters from start
            item = re.sub(r'^[^a-zA-Z]+', '', item)
            # Remove extra whitespace
            item = re.sub(r'\s+', ' ', item).strip()
            # Only include items with more than 3 words and containing letters
            if len(item.split()) > 3 and re.search(r'[a-zA-Z]', item):
                cleaned.append(item)
        
        return cleaned[:5]  # Keep only top 5 items as per model requirement
    
    def extract(self, text: str) -> ExtraCurricular:
        """Extract extra-curricular information from text."""
        extracted = {}
        lines = text.split('\n')
        
        # Extract each section
        for section, patterns in self.section_patterns.items():
            section_items = []
            bounds = self._find_section_bounds(text, patterns)
            
            for start, end in bounds:
                section_lines = lines[start:end]
                items = self._extract_items(section_lines)
                section_items.extend(items)
            
            extracted[section] = self._clean_items(section_items)
        
        # Create ExtraCurricular object with extracted data
        return ExtraCurricular(
            leadership=extracted.get('leadership', []),
            awards=extracted.get('awards', []),
            certifications=extracted.get('certifications', []),
            activities=extracted.get('activities', []),
            languages=extracted.get('languages', [])
        )
