import os
from google import genai

def analyze_resume_with_gemini(resume_text, job_description):
    """
    Sends the extracted resume text and job description to Gemini 
    to get smart AI feedback and a qualitative matching review.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key is not configured."

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert technical recruiter and AI hiring assistant. 
    Analyze the following candidate resume text against the target job description.
    
    JOB DESCRIPTION:
    {job_description}
    
    CANDIDATE RESUME:
    {resume_text}
    
    Provide a concise evaluation structured as follows:
    1. **Suitability Score (0-100%):** Give an estimated fit percentage.
    2. **Key Strengths:** Bullet points of matching skills/experience.
    3. **Gaps / Recommendations:** Missing skills or areas to improve.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini AI: {str(e)}"