from gemini_service import GeminiService
ai = GeminiService()

reply = ai.generate(

    "Hello! Introduce yourself in one sentence."

)

print(reply)