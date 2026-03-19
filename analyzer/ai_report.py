from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

def generate_ai_report(report_data):
    """
    Generate AI career advice based on portfolio analysis data.
    Falls back to template-based advice if OpenAI is unavailable.
    """
    
    # Check if OpenAI API key is properly configured
    if not openai_api_key or "your_openai_api_key_here" in openai_api_key.lower() or "your_" in openai_api_key.lower():
        logger.warning("OpenAI API key not configured, using fallback advice")
        return get_fallback_advice(report_data)
    
    try:
        client = OpenAI(api_key=openai_api_key)
        
        prompt = f"""
        Analyze this developer portfolio data and provide actionable career advice:

        Portfolio Score: {report_data['score']}/100
        Total Repositories: {report_data['repo_count']}
        Total Stars: {report_data['stars']}
        Programming Languages: {', '.join(report_data.get('languages', []))}
        Top Languages: {', '.join([lang.get('name', 'Unknown') for lang in report_data.get('top_languages', [])])}

        Please provide:
        1. Key strengths based on their GitHub activity
        2. Areas for improvement 
        3. 3 specific project suggestions to enhance their portfolio
        4. Career advice tailored to their experience level

        Keep the response concise, encouraging, and actionable. Format with clear headings.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using more stable model
            messages=[
                {"role": "system", "content": "You are a career advisor for developers. Provide helpful, actionable advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_advice = response.choices[0].message.content
        logger.info("Successfully generated AI career advice")
        return ai_advice
        
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return get_fallback_advice(report_data)
    except Exception as e:
        logger.error(f"Unexpected error generating AI advice: {e}")
        return get_fallback_advice(report_data)

def get_fallback_advice(report_data):
    """
    Generate template-based career advice when OpenAI is unavailable.
    """
    score = report_data.get('score', 0)
    repo_count = report_data.get('repo_count', 0)
    languages = report_data.get('languages', [])
    
    advice = []
    
    # Score-based advice
    if score >= 70:
        advice.append("**Great Progress!** Your portfolio shows strong activity and engagement.")
    elif score >= 40:
        advice.append("**Good Foundation!** You're building a solid presence on GitHub.")
    else:
        advice.append("**Growing Potential!** Every developer starts somewhere - keep building!")
    
    # Repository advice
    if repo_count < 5:
        advice.append("**Expand Your Portfolio:** Consider creating more diverse projects to showcase your skills.")
    elif repo_count < 20:
        advice.append("**Maintain Quality:** Focus on well-documented, complete projects rather than quantity.")
    else:
        advice.append("**Showcase Your Best:** Consider featuring your top projects prominently in your profile.")
    
    # Language advice
    if len(languages) == 1:
        advice.append(f"**Diversify Skills:** While expertise in {languages[0]} is valuable, explore additional technologies to broaden your opportunities.")
    elif len(languages) > 5:
        advice.append("**Focus on Strengths:** Consider specializing in 2-3 core languages rather than spreading too thin.")
    else:
        advice.append("**Balanced Approach:** Your multi-language experience is attractive to employers.")
    
    # Universal advice
    advice.extend([
        "**Documentation Matters:** Add README files and proper documentation to all projects.",
        "**Contribute to Open Source:** Even small contributions can significantly boost your visibility.",
        "**Build Network:** Engage with other developers through comments, issues, and collaborations."
    ])
    
    return "\n\n".join(advice)