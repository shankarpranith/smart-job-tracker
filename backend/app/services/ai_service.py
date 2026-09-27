from app.services.bedrock_service import invoke_claude_json


def analyze_job_description(job_description: str) -> dict:
    """
    Extract structured information from a raw job description using Claude.
    Returns required skills, preferred skills, experience level,
    technologies, and responsibilities.
    """
    prompt = f"""You are analyzing a job description for a job application tracker. Extract the following information and respond with ONLY a valid JSON object, no other text, no markdown formatting:

{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "experience_level": "e.g. Entry-level, Mid-level, Senior",
  "technologies": ["tech1", "tech2"],
  "responsibilities": ["responsibility1", "responsibility2"]
}}

Job Description:
{job_description}

Respond with ONLY the JSON object described above."""

    return invoke_claude_json(prompt, max_tokens=1500)
  
def match_resume_to_job(resume_text: str, job_description: str) -> dict:
    """
    Compare a resume against a job description using Claude.
    Returns match percentage, matching/missing skills, strengths,
    weaknesses, and recommendations.
    """
    prompt = f"""You are comparing a resume against a job description for a job application tracker. Respond with ONLY a valid JSON object, no other text, no markdown formatting:

{{
  "match_percentage": 0-100 (integer),
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": ["recommendation1", "recommendation2"]
}}

Job Description:
{job_description}

Resume:
{resume_text}

Respond with ONLY the JSON object described above."""

    return invoke_claude_json(prompt, max_tokens=1500)