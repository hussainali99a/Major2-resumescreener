import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from recruiter.services.schemas import ResumeEvaluation


MODEL_NAME = os.getenv('LLM_MODEL_NAME')


def run_resume_screening(resume_text: str, job_description: str):
    parser = PydanticOutputParser(pydantic_object=ResumeEvaluation)

    PROMPT = PromptTemplate(
        template="""
    You are an AI recruitment analyst.

    Extract structured information from the resume AND evaluate it against the job.

    Extract:
    - Candidate name
    - Email
    - Phone
    - LinkedIn, GitHub, portfolio links
    - Skills (all, demonstrated, listed-only)
    - Experience in years
    - Strengths and gaps
    - Match score & recommendation

    Scoring:
    0.8+ strong
    0.6–0.79 good
    0.4–0.59 moderate
    <0.4 weak

    Recommendation:
    >=0.65 ACCEPT
    0.5–0.64 HOLD
    <0.5 REJECT

    Return ONLY valid JSON matching this schema:
    {format_instructions}

    Resume:
    {resume}

    Job Description:
    {job}
    """,
        input_variables=["resume", "job"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
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