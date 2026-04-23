import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from recruiter.services.schemas import ResumeEvaluation


MODEL_NAME = os.getenv('LLM_MODEL_NAME')


def run_resume_screening(resume_text: str, job_description: str):
    parser = PydanticOutputParser(pydantic_object=ResumeEvaluation)

    PROMPT = PromptTemplate(template="""
    You are a strict Applicant Tracking System (ATS).

    Evaluate the resume ONLY against the Job Description (JD) using keyword and experience matching.

    Rules:
    - Use ONLY explicit information from the resume. Do NOT infer.
    - Match keywords EXACTLY from JD (minor variations allowed: e.g., REST API ≈ RESTful API).
    - Penalize missing required skills heavily.
    - Penalize vague terms ("familiar with", "worked on").
    - Reward clear, technical, and measurable contributions.
    - Experience must align with JD requirements (years + relevance).

    Scoring Weights:
    - Skills: 50%
    - Experience: 30%
    - Projects: 20%

    Scoring Output (0–1 scale):
    - >=0.8 strong
    - 0.6–0.79 good
    - 0.4–0.59 moderate
    - <0.4 weak

    Recommendation:
    - >=0.65 ACCEPT
    - 0.5–0.64 HOLD
    - <0.5 REJECT

    Extraction Requirements:
    - Candidate name, email, phone
    - Links (LinkedIn, GitHub, portfolio)
    - Skills (all, demonstrated, listed-only)
    - Total experience (years)
    - Strengths (based on JD match)
    - Gaps (missing JD requirements)

    Strict Constraints:
    - No assumptions
    - No extra explanation
    - No conversational text
    - Output MUST be valid JSON only

    {format_instructions}

    Resume:
    {resume}

    Job Description:
    {job}
    """,
        input_variables=["resume", "job"], 
        partial_variables={ "format_instructions": parser.get_format_instructions()}
    )
    # ---- LLM ----
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # ---- Chain ----
    chain = PROMPT | llm | parser

    result = chain.invoke({
        "resume": resume_text,
        "job": job_description
    })

    return result