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
        
        prompt = f"""You are an expert software engineering career evaluator and technical recruiter.

Analyze the following GitHub profile data in EXTREME DETAIL and generate a premium-level report that feels like a paid professional audit.

GitHub Data:
{report_data}

---

Generate a highly detailed report with these sections:

1. 🔍 Overall Developer Score (0–100)
* Give a realistic score based on hireability
* Explain clearly why this score was given

2. 🧠 Skill Assessment
* Identify programming languages used
* Frameworks and tools detected
* Skill level (Beginner / Intermediate / Advanced)
* Depth vs breadth of skills

3. 📁 Project Quality Analysis
* Evaluate best projects
* Code quality and structure
* Real-world usefulness
* Originality vs tutorial-based projects

4. 📊 Consistency & Activity
* Commit frequency
* Contribution patterns
* Growth over time

5. 🏆 Strengths
* Clear bullet points of strong areas
* What stands out to recruiters

6. ⚠️ Weaknesses
* Be brutally honest
* What is missing or weak

7. 💼 Hireability Analysis
* Would this person get hired? Why or why not?
* What level of companies they can get into (startup / mid / top-tier)

8. 🚀 Improvement Roadmap (VERY IMPORTANT)
* Exact steps to improve profile
* What projects to build next
* What skills to learn
* Prioritized action plan

9. 💡 Portfolio Suggestions
* 3–5 specific high-value project ideas
* Ideas that increase hiring chances FAST

10. 👔 Recruiter Impression Summary
* Short 3–4 line summary of first impression

11. 📈 Final Verdict
* Overall level and next milestone

IMPORTANT:
* Be specific, not generic
* Avoid vague advice
* Make it feel like a premium ₹5000 report
* Be honest and slightly critical where needed
* Use clear formatting and bullet points
* Provide concrete examples where possible

Format response using markdown with clear headings and bullet points."""

        response = client.chat.completions.create(
            model="gpt-4",  # Using more capable model for detailed analysis
            messages=[
                {"role": "system", "content": "You are an expert software engineering career evaluator and technical recruiter. Provide comprehensive, detailed, and actionable career analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,  # Increased for detailed premium report
            temperature=0.3  # Lower for more consistent, professional output
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