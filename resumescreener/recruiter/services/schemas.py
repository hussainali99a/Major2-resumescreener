from pydantic import BaseModel, Field
from typing import List, Optional

class ResumeEvaluation(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""

    match_score: float
    reasoning: str
    strengths: List[str]
    gaps: List[str]

    demonstrated_skills: List[str]
    listed_skills_only: List[str]
    all_skills: List[str]

    experience_years: float
    recommendation: str