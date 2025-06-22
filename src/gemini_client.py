import google.generativeai as genai
from .config import GEMINI_API_KEY
from .prompts import SOCIONICS_PROMPT_TEMPLATE, HYPOTHESIS_PROMPT_SECTION

genai.configure(api_key=GEMINI_API_KEY)

# Настройки генерации
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192, # Максимальная длина ответа
}

# Настройки безопасности
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

async def get_socionics_analysis(messages_text: str, hypothesis: str | None = None) -> str:
    """
    Отправляет текст в Gemini и получает анализ.
    """
    hypothesis_section = ""
    if hypothesis:
        hypothesis_section = HYPOTHESIS_PROMPT_SECTION.format(hypothesis=hypothesis)

    prompt = SOCIONICS_PROMPT_TEMPLATE.format(
        messages_text=messages_text,
        hypothesis_section=hypothesis_section
    )
    
    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Ошибка при обращении к Gemini API: {e}")
        return f"Произошла ошибка при генерации ответа. Пожалуйста, попробуйте позже.\n\nДетали ошибки: {e}"