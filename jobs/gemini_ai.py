import os
import time
from google import genai

def analyze_resume_with_gemini(resume_text, job_description):
    """
    Sends the extracted resume text and job description to Gemini 
    using the stable gemini-3.5-flash model endpoint.
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

    max_retries = 3
    delay = 2

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
            return f"Error communicating with Gemini AI: {str(e)}"
            
    return "Gemini AI service is temporarily unavailable due to high demand. Please try again in a moment."