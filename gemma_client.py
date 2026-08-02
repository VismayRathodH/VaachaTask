import os
import json
import re
import warnings

# Suppress the deprecation/future warning from google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from prompts import SYSTEM_PROMPT_EXTRACTION, SYSTEM_PROMPT_GENERATION

def configure_api(api_key: str = None):
    """Configures the Google GenAI SDK with the provided or environment-based key."""
    # Manually load .env file from current directory or app root on every call to avoid caching issues
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

    key = api_key or os.environ.get("GEMMA_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if key:
        genai.configure(api_key=key)
        return True
    return False



def extract_fields(text: str, api_key: str = None) -> dict:
    """Extracts structured JSON fields from the user input text using Gemini/Gemma model."""
    configured = configure_api(api_key)
    
    # Fallback response for demo safety if no key is set or API fails
    fallback_data = {
        "customer": "મનોજભાઈ",
        "action": "delivery",
        "quantity": "25 box",
        "due_date": "tomorrow",
        "amount": "₹12,500",
        "payment_status": "pending",
        "next_action": "Deliver 25 boxes and follow up on pending payment"
    }

    if not configured:
        # If no key, check if text matches the classic example to return a matching mock
        if "મનોજ" in text or "manoj" in text.lower():
            return fallback_data
        # Otherwise, generic mock
        return {
            "customer": "ગ્રાહક (નથી જણાવ્યું)",
            "action": "other",
            "quantity": None,
            "due_date": "આજે",
            "amount": None,
            "payment_status": None,
            "next_action": text
        }

    try:
        # Use the hackathon Gemma 4 model
        model = genai.GenerativeModel("gemma-4-31b-it")
        
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [SYSTEM_PROMPT_EXTRACTION + "\n\nInput: " + text]}
            ]
        )
        
        raw_text = response.text.strip()
        
        # Robust JSON extraction: find ALL {...} blocks and try last-first
        # Gemma 4 outputs thinking/reasoning before the final JSON answer
        json_candidates = []
        depth = 0
        start_idx = None
        for i, ch in enumerate(raw_text):
            if ch == '{':
                if depth == 0:
                    start_idx = i
                depth += 1
            elif ch == '}':
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start_idx is not None:
                        json_candidates.append(raw_text[start_idx:i+1])
                        start_idx = None
        
        # Try candidates from last to first (Gemma puts the clean answer last)
        for candidate in reversed(json_candidates):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Fallback: try markdown code blocks
        matches = re.findall(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
        for match in reversed(matches):
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                pass
        
        # Last resort: direct parse
        return json.loads(raw_text)

    except Exception as e:
        print(f"Error during extraction API call: {e}")

        # Return fallback/mock
        return {
            "customer": "ભૂલ આવી / કનેક્શન પ્રોબ્લેમ",
            "action": "other",
            "quantity": None,
            "due_date": None,
            "amount": None,
            "payment_status": None,
            "next_action": f"Error: {str(e)}"
        }

def generate_confirmation(fields: dict, api_key: str = None) -> str:
    """Generates a natural Gujarati confirmation message from structured fields."""
    configured = configure_api(api_key)
    
    if not configured:
        # Fallback response generator if API fails
        cust = fields.get("customer") or "ગ્રાહક"
        # Avoid duplicating honorific suffixes
        if not any(cust.endswith(suffix) for suffix in ["ભાઈ", "બેન", "જી", "bhai", "ben", "ji"]):
            cust_formatted = f"{cust}ભાઈ"
        else:
            cust_formatted = cust

        action = fields.get("action")
        amt = fields.get("amount")
        qty = fields.get("quantity")
        due = fields.get("due_date") or "ટૂંક સમયમાં"
        
        if action == "delivery":
            msg = f"{cust_formatted}, નમસ્તે. તમારા {qty or 'ઓર્ડર'} ની ડિલિવરી {due} કરવામાં આવશે."
            if amt:
                msg += f" ચુકવણી બાકી રકમ {amt} છે. કૃપા કરી સરભર કરશો. આભાર!"
            return msg
        elif action == "payment reminder":
            return f"{cust_formatted}, નમસ્તે. આપણી બાકી ચુકવણી {amt or ''} ની સમયમર્યાદા {due} સુધીની છે. કૃપા કરી જલ્દી પેમેન્ટ કરવા વિનંતી. આભાર!"
        elif action == "order":
            return f"{cust_formatted}, નમસ્તે. તમારો {qty or 'સામાન'} નો ઓર્ડર મળી ગયો છે. વિગતવાર માહિતી ટૂંક સમયમાં મોકલીશું."
        else:
            return f"{cust_formatted}, નમસ્તે. {fields.get('next_action') or 'સંદર્ભે નોંધ લેવામાં આવી છે.'} આભાર!"


    try:
        model = genai.GenerativeModel("gemma-4-31b-it")
        fields_json = json.dumps(fields, ensure_ascii=False, indent=2)
        
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [SYSTEM_PROMPT_GENERATION.format(fields=fields_json)]}
            ]
        )
        raw_output = response.text.strip()
        
        # Split into paragraph blocks separated by blank lines
        # Gemma 4 always writes the clean final answer in the LAST paragraph block
        paragraph_blocks = re.split(r'\n\s*\n', raw_output)
        
        gujarati_blocks = []
        for block in paragraph_blocks:
            # Keep only lines that contain Gujarati characters, skip pure-English reasoning
            block_lines = block.split('\n')
            gujarati_lines = []
            for line in block_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                # Skip pure English/reasoning lines, keep Gujarati-containing lines
                if re.search(r'[\u0a80-\u0aff]', stripped):
                    # Also skip lines starting with bullet/list markers
                    if not (stripped.startswith("*") or stripped.startswith("-")):
                        gujarati_lines.append(stripped)
            if gujarati_lines:
                gujarati_blocks.append("\n".join(gujarati_lines))
        
        if gujarati_blocks:
            # The last Gujarati block is the final clean message
            return gujarati_blocks[-1].strip()
        
        return raw_output.strip()



    except Exception as e:
        print(f"Error during generation API call: {e}")
        return f"સંદેશ જનરેટ કરવામાં ભૂલ આવી: {str(e)}"

def transcribe_audio(audio_file, api_key: str = None) -> str:
    """Transcribes recorded audio to text.
    
    Strategy:
    1. Google Speech Recognition via SpeechRecognition library (free, no quota, supports gu-IN)
    2. Gemini multimodal fallback (if quota allows)
    """
    import io
    
    # Read audio bytes once
    audio_bytes = audio_file.read()
    mime_type = getattr(audio_file, 'type', None) or "audio/wav"
    
    # --- Method 1: Google Speech Recognition (free, no API quota) ---
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = r.record(source)
        
        # Try Gujarati first, then mixed Gujarati-English
        for lang in ["gu-IN", "en-IN"]:
            try:
                result = r.recognize_google(audio_data, language=lang)
                if result:
                    return result
            except sr.UnknownValueError:
                continue
            except sr.RequestError as re_err:
                print(f"Google Speech API error for {lang}: {re_err}")
                break
    except ImportError:
        print("SpeechRecognition not installed.")
    except Exception as e:
        print(f"SpeechRecognition failed: {e}")

    # --- Method 2: Gemini multimodal (falls back if SR unavailable) ---
    try:
        configure_api(api_key)
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        # Try models in order of preference
        for model_name in ["gemma-4-31b-it", "gemini-2.0-flash"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": mime_type,
                                        "data": audio_b64
                                    }
                                },
                                "Transcribe the spoken audio exactly as heard. If Gujarati or mixed Gujarati-English, preserve it as-is. Output only the transcription text."
                            ]
                        }
                    ]
                )
                if response.text:
                    return response.text.strip()
            except Exception as model_err:
                print(f"Gemini model {model_name} transcription error: {model_err}")
                continue
    except Exception as e:
        print(f"Gemini fallback failed: {e}")
    
    return "ઑડિઓ ટ્રાન્સક્રાઇબ થઈ શક્યો નહિ. કૃપા કરી ફરીથી પ્રયત્ન કરો."


