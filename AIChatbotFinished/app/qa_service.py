import os
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            max_output_tokens=1024,
        )
    )
else:
    model = None


def answer_query(question: str) -> str:
    try:
        if not model:
            return "Error: Google AI service not properly configured"

        enhanced_query = f"""You are a University of Birmingham academic advisor AI. Provide accurate, specific answers based on the official regulations provided. Always:

1. Give direct, factual responses based on the regulations
2. Use specific numbers, percentages, and deadlines when available
3. Explain consequences clearly (e.g., "cannot progress", "must resit")
4. Distinguish between different types of failures and their implications
5. Be precise about credit requirements and calculations

{question}

Response:"""

        response = model.generate_content(enhanced_query)

        if response and response.text:
            cleaned_response = response.text.strip()

            if "I don't have enough information" in cleaned_response and "credits" in question.lower():
                return "Based on Birmingham University regulations: If you fail modules, you need at least 100 credits to progress to the next year. Each module is typically worth 20 credits. Please provide more specific details for a precise assessment, or contact your School office for personalized guidance."

            return cleaned_response
        else:
            return "Error: No response generated"

    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return "The AI service is temporarily busy. Please try again in a moment."
        elif "connection" in error_msg.lower():
            return "Connection issue with AI service. Please check your internet and try again."
        else:
            return f"Error: {error_msg}"


def validate_query(query: str) -> bool:
    if not query or len(query.strip()) < 3:
        return False
    if len(query) > 2000:
        return False
    return True


def preprocess_query(query: str) -> str:
    query = query.replace("soft fail", "fail")
    query = query.replace("courses", "modules")
    query = query.replace("class", "module")
    query = query.replace("subject", "module")

    return query.strip()