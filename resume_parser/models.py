from typing import List, Optional
from pydantic import BaseModel, Field

class StudentMetadata(BaseModel):
    name: str = Field(..., description='Student name')
    gender: str = Field(..., description='Student gender')
    reg_no: str = Field(..., description='Student registration number')
    dob: str = Field(..., description='Student date of birth')
    email: str = Field(..., description='Student date of birth')
    phone: str = Field(..., description='Student phone number')
    mobile: str = Field(..., description='Student mobile number')
    branch: str = Field(..., description='Student branch')
    degree: str = Field(..., description='Student degree')

class AcademicDegreePerformance(BaseModel):
    semester: int = Field(..., description='Semester number')
    duration: str = Field(..., description='Semester month and year')
    sgpa: float = Field(..., description='Semester sgpa')
    cgpa: float = Field(..., description='Semester cgpa')
    degree: str = Field(..., description='Degree')

class TechnicalSkills(BaseModel):
    programming_languages: List[str] = Field(default=[], description='List of programming languages known')
    frameworks: List[str] = Field(default=[], description='List of programming language frameworks known')
    databases: List[str] = Field(default=[], description='List of databases known')
    other_technologies: List[str] = Field(default=[], description='List of other tools and technologies')
    knowledge_area: List[str] = Field(default=[], description='Organized sets of information used for the execution of tasks and activities within a particular domain, e.g., web design, cyber security, statistics, api, gui, game developement,  etc')

class Projects(BaseModel):
    name: str = Field(..., description='short name for the project or research publication')
    company: str = Field(..., description='internship or training company')
    duration: str = Field(..., description='duration of the training or internship')
    skill: TechnicalSkills

class ExtraCurricular(BaseModel):
    leadership: List[str] = Field(default=[], description='List of leadership positions held, keep it short witin 5 words')
    awards: List[str] = Field(default=[], description='List of awards and achievements, keep it short witin 5 words')
    certifications: List[str] = Field(default=[], description='List of certifications, keep it short witin 5 words')
    activities: List[str] = Field(default=[], description='List of activities like sports, cultural, etc, keep it short witin 5 words')
    languages: List[str] = Field(default=[], description='List of spoken languages known, keep it short witin 5 words')

class ResumeInfo(BaseModel):
    metadata: StudentMetadata
    academic_performance: List[AcademicDegreePerformance]
    projects: List[Projects]
    technical_skills: TechnicalSkills
    