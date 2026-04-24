import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_resume(resume_text, user_goal):
    try:
        # Initialize the model (using flash for speed and cost efficiency)
        model = genai.GenerativeModel('gemini-3-flash-preview')

        # Define the prompt
        prompt = f"""
        Analyze this resume for the goal: {user_goal}.
        Return ONLY valid JSON in this format:
        {{
            "skills": ["skill1", "skill2"],
            "missing_skills": ["skill3", "skill4"],
            "roadmap": ["step1", "step2"],
            "interview_questions": ["q1", "q2", "q3"]
        }}
        Resume: {resume_text}
        """

        # Generate content with JSON enforcement
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        return json.loads(response.text)

    except Exception as e:
        return {
            "skills": ["Error"], 
            "missing_skills": [str(e)], 
            "roadmap": ["Error"], 
            "interview_questions": ["Error"]
        }