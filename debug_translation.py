from deep_translator import GoogleTranslator

try:
    text = "Good student"
    result = GoogleTranslator(source='auto', target='te').translate(text)
    print(f"Original: {text}")
    print(f"Translated: {result}")
except Exception as e:
    print(f"Error: {e}")
