import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

class GeminiTranslator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def translate_university_names(self, universities, country="Poland", language="Polish"):
        """
        universities: list of dicts with {'chinese_name': ..., 'original_name': ...}
        returns: list of dicts with {'chinese_name': ..., 'english_name': ...}
        """
        prompt = (
            f"You are an expert academic translator. I will provide a list of universities in {country}. "
            f"Each entry contains a 'chinese_name' and an 'original_name' (in {language}). "
            f"Please provide the official, most commonly used international English name for each university "
            f"based primarily on the 'original_name', using the 'chinese_name' only as secondary context. "
            "Respond strictly in JSON format as a list of objects, each containing the original 'chinese_name' and the new 'english_name'.\n\n"
            f"Data: {json.dumps(universities, ensure_ascii=False)}"
        )
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            
            # Validation: Ensure it's a list and has required keys
            if not isinstance(data, list):
                print(f"Warning: Gemini returned non-list data: {response.text}")
                return []
            
            validated_data = []
            for item in data:
                if isinstance(item, dict) and 'chinese_name' in item and 'english_name' in item:
                    # Filter out error messages that might be in the text
                    ename = str(item['english_name']).lower()
                    if any(err in ename for err in ["error", "unknown", "n/a", "cannot translate"]):
                        print(f"Warning: Gemini returned suspicious name for {item['chinese_name']}: {item['english_name']}")
                        continue
                    validated_data.append(item)
            
            return validated_data
        except Exception as e:
            print(f"Error calling Gemini or parsing response: {e}")
            return []

if __name__ == "__main__":
    # Test
    translator = GeminiTranslator()
    test_data = [{"chinese_name": "奥波莱大学", "original_name": "Uniwersytet Opolski"}]
    print(translator.translate_university_names(test_data))
