"""
Parent Eye - A Real-Time Child Monitoring and Alert System for Enhanced Parental Awareness
Main Flask Application
"""

import os
import io
from flask import Flask, request, jsonify, render_template, session, send_file
from flask_cors import CORS
from models import predictor
from chatbot import chatbot

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'parent-eye-secret-key-2026')
CORS(app)

SUPPORTED_LANGS = {'en', 'te', 'hi', 'ta'}
DEFAULT_LANG = 'en'


def normalize_lang(lang):
    """Return a supported app language code."""
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def json_payload():
    """Read JSON request bodies without raising on empty or invalid input."""
    return request.get_json(silent=True) or {}


# ─── Demo Data ────────────────────────────────────────────────────────────────

DEMO_USERS = {
    "parent1": {
        "password": "pass123",
        "name": "Rajesh Kumar",
        "child_name": "Arjun Kumar",
        "class": "10th Standard",
        "section": "A",
        "roll_no": 15,
        "school": "Vidya Bharathi High School"
    },
    "parent2": {
        "password": "pass123",
        "name": "Lakshmi Devi",
        "child_name": "Priya Lakshmi",
        "class": "10th Standard",
        "section": "B",
        "roll_no": 22,
        "school": "Vidya Bharathi High School"
    }
}

STUDENT_DATA = {
    "parent1": {
        "marks": {
            "Mathematics": 85,
            "Science": 78,
            "English": 72,
            "Telugu": 88,
            "Hindi": 70,
            "Social Studies": 82
        },
        "marks_history": {
            "Mathematics": [72, 75, 80, 83, 85],
            "Science": [65, 68, 72, 75, 78],
            "English": [60, 63, 67, 70, 72],
            "Telugu": [80, 82, 85, 86, 88],
            "Hindi": [62, 65, 67, 68, 70],
            "Social Studies": [70, 73, 76, 79, 82]
        },
        "attendance": 92,
        "total_classes": 180,
        "attended_classes": 166,
        "rank": 5,
        "total_students": 45,
        "remarks": "Good student with consistent improvement. Needs to focus more on English and Hindi.",
        "notifications": [
            {"type": "exam", "message": "Final-term exams start from May 20, 2026", "date": "2026-05-04"},
            {"type": "meeting", "message": "Parent-Teacher meeting on May 10, 2026 at 10:00 AM", "date": "2026-05-03"},
            {"type": "achievement", "message": "Won 2nd prize in Science Exhibition!", "date": "2026-04-30"}
        ]
    },
    "parent2": {
        "marks": {
            "Mathematics": 92,
            "Science": 88,
            "English": 85,
            "Telugu": 90,
            "Hindi": 82,
            "Social Studies": 87
        },
        "marks_history": {
            "Mathematics": [82, 85, 88, 90, 92],
            "Science": [78, 80, 83, 85, 88],
            "English": [75, 78, 80, 82, 85],
            "Telugu": [82, 84, 86, 88, 90],
            "Hindi": [70, 73, 76, 79, 82],
            "Social Studies": [78, 80, 83, 85, 87]
        },
        "attendance": 96,
        "total_classes": 180,
        "attended_classes": 173,
        "rank": 2,
        "total_students": 42,
        "remarks": "Excellent student with outstanding performance. Class topper material!",
        "notifications": [
            {"type": "exam", "message": "Final-term exams start from May 20, 2026", "date": "2026-05-04"},
            {"type": "achievement", "message": "Selected for State-level Math Olympiad!", "date": "2026-05-01"},
            {"type": "meeting", "message": "Parent-Teacher meeting on May 10, 2026 at 10:00 AM", "date": "2026-05-03"}
        ]
    }
}

# ─── Translation dictionary for UI elements ──────────────────────────────────

UI_TRANSLATIONS = {
    "en": {
        "app_title": "Parent Eye",
        "login_title": "Parent Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "demo_info": "Demo: parent1 / pass123",
        "dashboard": "Dashboard",
        "welcome": "Welcome",
        "child_info": "Student Information",
        "child_name": "Student Name",
        "class": "Class",
        "section": "Section",
        "roll_no": "Roll Number",
        "school": "School",
        "marks_overview": "Marks Overview",
        "attendance": "Attendance",
        "rank": "Class Rank",
        "total_students": "Total Students",
        "predictions": "AI Predictions",
        "predict_btn": "Predict Future Marks",
        "predicted_mark": "Predicted Mark",
        "trend": "Performance Trend",
        "confidence": "Confidence",
        "notifications": "Notifications",
        "chatbot": "Chat Assistant",
        "type_message": "Type your message...",
        "send": "Send",
        "speak": "Speak",
        "logout": "Logout",
        "language": "Language",
        "marks_trend": "Marks Trend",
        "subject": "Subject",
        "mark": "Marks",
        "remarks": "Teacher Remarks",
        "improving": "Improving",
        "declining": "Declining",
        "stable": "Stable",
        "semester": "Test",
        "enter_past_marks": "Enter past marks (comma separated)",
        "chatbot_welcome": "Hello! I'm your Parent Eye assistant. Ask me about marks, attendance, predictions, or anything about your child's education!",
        "voice_input": "Voice Input",
        "total_classes": "Total Classes",
        "attended": "Attended",
        "select_language": "Select Language"
    },
    "te": {
        "app_title": "Parent Eye",
        "login_title": "తల్లిదండ్రుల లాగిన్",
        "username": "యూజర్‌నేమ్",
        "password": "పాస్‌వర్డ్",
        "login_btn": "లాగిన్",
        "demo_info": "డెమో: parent1 / pass123",
        "dashboard": "డాష్‌బోర్డ్",
        "welcome": "స్వాగతం",
        "child_info": "విద్యార్థి సమాచారం",
        "child_name": "విద్యార్థి పేరు",
        "class": "తరగతి",
        "section": "సెక్షన్",
        "roll_no": "రోల్ నంబర్",
        "school": "పాఠశాల",
        "marks_overview": "మార్కుల సారాంశం",
        "attendance": "హాజరు",
        "rank": "తరగతి ర్యాంక్",
        "total_students": "మొత్తం విద్యార్థులు",
        "predictions": "AI అంచనాలు",
        "predict_btn": "భవిష్యత్ మార్కులు అంచనా",
        "predicted_mark": "అంచనా మార్కు",
        "trend": "పనితీరు ధోరణి",
        "confidence": "నమ్మకం",
        "notifications": "నోటిఫికేషన్లు",
        "chatbot": "చాట్ సహాయకుడు",
        "type_message": "మీ సందేశాన్ని టైప్ చేయండి...",
        "send": "పంపు",
        "speak": "మాట్లాడు",
        "logout": "లాగ్‌అవుట్",
        "language": "భాష",
        "marks_trend": "మార్కుల ధోరణి",
        "subject": "సబ్జెక్టు",
        "mark": "మార్కులు",
        "remarks": "ఉపాధ్యాయ వ్యాఖ్యలు",
        "improving": "మెరుగుపడుతోంది",
        "declining": "తగ్గుతోంది",
        "stable": "స్థిరంగా",
        "semester": "పరీక్ష",
        "enter_past_marks": "గత మార్కులు నమోదు చేయండి (కామాతో వేరు చేయండి)",
        "chatbot_welcome": "నమస్కారం! నేను మీ Parent Eye సహాయకుడిని. మార్కులు, హాజరు, అంచనాలు లేదా మీ బిడ్డ విద్య గురించి ఏదైనా అడగండి!",
        "voice_input": "వాయిస్ ఇన్‌పుట్",
        "total_classes": "మొత్తం తరగతులు",
        "attended": "హాజరైన",
        "select_language": "భాషను ఎంచుకోండి"
    },
    "hi": {
        "app_title": "Parent Eye",
        "login_title": "अभिभावक लॉगिन",
        "username": "यूज़रनेम",
        "password": "पासवर्ड",
        "login_btn": "लॉगिन",
        "demo_info": "डेमो: parent1 / pass123",
        "dashboard": "डैशबोर्ड",
        "welcome": "स्वागत है",
        "child_info": "छात्र जानकारी",
        "child_name": "छात्र का नाम",
        "class": "कक्षा",
        "section": "अनुभाग",
        "roll_no": "रोल नंबर",
        "school": "विद्यालय",
        "marks_overview": "अंक सारांश",
        "attendance": "उपस्थिति",
        "rank": "कक्षा रैंक",
        "total_students": "कुल छात्र",
        "predictions": "AI भविष्यवाणी",
        "predict_btn": "भविष्य के अंक का अनुमान",
        "predicted_mark": "अनुमानित अंक",
        "trend": "प्रदर्शन रुझान",
        "confidence": "विश्वास",
        "notifications": "सूचनाएं",
        "chatbot": "चैट सहायक",
        "type_message": "अपना संदेश टाइप करें...",
        "send": "भेजें",
        "speak": "बोलें",
        "logout": "लॉगआउट",
        "language": "भाषा",
        "marks_trend": "अंक रुझान",
        "subject": "विषय",
        "mark": "अंक",
        "remarks": "शिक्षक टिप्पणी",
        "improving": "सुधार हो रहा है",
        "declining": "गिरावट",
        "stable": "स्थिर",
        "semester": "परीक्षा",
        "enter_past_marks": "पिछले अंक दर्ज करें (कॉमा से अलग करें)",
        "chatbot_welcome": "नमस्ते! मैं आपका Parent Eye सहायक हूं। अंक, उपस्थिति, भविष्यवाणी या अपने बच्चे की शिक्षा के बारे में कुछ भी पूछें!",
        "voice_input": "वॉइस इनपुट",
        "total_classes": "कुल कक्षाएं",
        "attended": "उपस्थित",
        "select_language": "भाषा चुनें"
    },
    "ta": {
        "app_title": "Parent Eye",
        "login_title": "பெற்றோர் உள்நுழைவு",
        "username": "பயனர்பெயர்",
        "password": "கடவுச்சொல்",
        "login_btn": "உள்நுழை",
        "demo_info": "டெமோ: parent1 / pass123",
        "dashboard": "டாஷ்போர்டு",
        "welcome": "வரவேற்கிறோம்",
        "child_info": "மாணவர் தகவல்",
        "child_name": "மாணவர் பெயர்",
        "class": "வகுப்பு",
        "section": "பிரிவு",
        "roll_no": "ரோல் எண்",
        "school": "பள்ளி",
        "marks_overview": "மதிப்பெண் சுருக்கம்",
        "attendance": "வருகைப்பதிவு",
        "rank": "வகுப்பு தரவரிசை",
        "total_students": "மொத்த மாணவர்கள்",
        "predictions": "AI கணிப்புகள்",
        "predict_btn": "எதிர்கால மதிப்பெண் கணிப்பு",
        "predicted_mark": "கணிக்கப்பட்ட மதிப்பெண்",
        "trend": "செயல்திறன் போக்கு",
        "confidence": "நம்பிக்கை",
        "notifications": "அறிவிப்புகள்",
        "chatbot": "அரட்டை உதவியாளர்",
        "type_message": "உங்கள் செய்தியை தட்டச்சு செய்யுங்கள்...",
        "send": "அனுப்பு",
        "speak": "பேசு",
        "logout": "வெளியேறு",
        "language": "மொழி",
        "marks_trend": "மதிப்பெண் போக்கு",
        "subject": "பாடம்",
        "mark": "மதிப்பெண்",
        "remarks": "ஆசிரியர் கருத்துகள்",
        "improving": "முன்னேறுகிறது",
        "declining": "குறைகிறது",
        "stable": "நிலையான",
        "semester": "தேர்வு",
        "enter_past_marks": "கடந்த மதிப்பெண்களை உள்ளிடுங்கள் (காற்புள்ளியால் பிரிக்கவும்)",
        "chatbot_welcome": "வணக்கம்! நான் உங்கள் Parent Eye உதவியாளர். மதிப்பெண்கள், வருகைப்பதிவு, கணிப்புகள் அல்லது உங்கள் குழந்தையின் கல்வி பற்றி எதையும் கேளுங்கள்!",
        "voice_input": "குரல் உள்ளீடு",
        "total_classes": "மொத்த வகுப்புகள்",
        "attended": "கலந்துகொண்ட",
        "select_language": "மொழியை தேர்ந்தெடுக்கவும்"
    }
}

# Subject name translations
SUBJECT_TRANSLATIONS = {
    "en": {
        "Mathematics": "Mathematics", "Science": "Science", "English": "English",
        "Telugu": "Telugu", "Hindi": "Hindi", "Social Studies": "Social Studies"
    },
    "te": {
        "Mathematics": "గణితం", "Science": "సైన్స్", "English": "ఇంగ్లీష్",
        "Telugu": "తెలుగు", "Hindi": "హిందీ", "Social Studies": "సాంఘిక శాస్త్రం"
    },
    "hi": {
        "Mathematics": "गणित", "Science": "विज्ञान", "English": "अंग्रेज़ी",
        "Telugu": "तेलुगु", "Hindi": "हिंदी", "Social Studies": "सामाजिक विज्ञान"
    },
    "ta": {
        "Mathematics": "கணிதம்", "Science": "அறிவியல்", "English": "ஆங்கிலம்",
        "Telugu": "தெலுங்கு", "Hindi": "இந்தி", "Social Studies": "சமூக அறிவியல்"
    }
}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/api/translations/<lang>')
def get_translations(lang):
    """Get UI translations for a specific language."""
    lang = normalize_lang(lang)
    return jsonify({
        "ui": UI_TRANSLATIONS[lang],
        "subjects": SUBJECT_TRANSLATIONS[lang]
    })


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate parent login."""
    data = json_payload()
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()

    if username in DEMO_USERS and DEMO_USERS[username]['password'] == password:
        user = DEMO_USERS[username]
        session['user'] = username
        return jsonify({
            "success": True,
            "user": {
                "name": user['name'],
                "child_name": user['child_name'],
                "class": user['class'],
                "section": user['section'],
                "roll_no": user['roll_no'],
                "school": user['school']
            }
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid username or password"
        }), 401


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Return student performance data."""
    username = request.args.get('user', 'parent1')
    lang = normalize_lang(request.args.get('lang', DEFAULT_LANG))
    if username not in STUDENT_DATA:
        return jsonify({"error": "User not found"}), 404

    data = STUDENT_DATA[username]
    user_info = DEMO_USERS.get(username, {})

    # Translate dynamic content if language is not English
    remarks = data['remarks']
    notifications = data['notifications']

    if lang != 'en':
        try:
            from deep_translator import GoogleTranslator
            
            # Translate remarks
            remarks = GoogleTranslator(source='auto', target=lang).translate(remarks)
            
            # Translate notifications
            translated_notifications = []
            for n in notifications:
                trans_msg = GoogleTranslator(source='auto', target=lang).translate(n['message'])
                translated_notifications.append({
                    "type": n['type'],
                    "message": trans_msg,
                    "date": n['date']
                })
            notifications = translated_notifications
        except Exception as e:
            print(f"Translation error: {e}")

    # Get predictions for all subjects
    predictions = predictor.predict_subject_wise(data['marks_history'])

    return jsonify({
        "student": {
            "name": user_info.get('child_name', 'Student'),
            "class": user_info.get('class', ''),
            "section": user_info.get('section', ''),
            "roll_no": user_info.get('roll_no', 0),
            "school": user_info.get('school', '')
        },
        "marks": data['marks'],
        "marks_history": data['marks_history'],
        "attendance": data['attendance'],
        "total_classes": data['total_classes'],
        "attended_classes": data['attended_classes'],
        "rank": data['rank'],
        "total_students": data['total_students'],
        "remarks": remarks,
        "notifications": notifications,
        "predictions": {
            subj: {
                "predicted_mark": pred['predicted_mark'],
                "trend": pred['trend'],
                "confidence": pred['confidence']
            }
            for subj, pred in predictions.items()
        }
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict future marks from past marks input."""
    data = json_payload()
    past_marks = data.get('past_marks', [])

    try:
        past_marks = [float(m) for m in past_marks]
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid marks format"}), 400

    result = predictor.predict_future_marks(past_marks)
    return jsonify(result)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot endpoint - responds to parent queries."""
    data = json_payload()
    message = str(data.get('message', ''))
    username = data.get('user', 'parent1')
    lang = normalize_lang(data.get('lang', DEFAULT_LANG))

    if not message.strip():
        return jsonify({"error": "Empty message"}), 400

    # Translate message to English if not already
    if lang != 'en':
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target='en').translate(message)
            message = translated
        except Exception as e:
            print(f"Input translation error: {e}")

    # Get student data for context
    student_data = STUDENT_DATA.get(username, STUDENT_DATA['parent1'])

    # Add prediction data to student context
    avg_marks = sum(student_data['marks'].values()) / len(student_data['marks'])
    marks_list = list(student_data['marks'].values())
    prediction = predictor.predict_future_marks(marks_list)

    enriched_data = {
        **student_data,
        "predicted_mark": prediction.get('predicted_mark', avg_marks),
        "trend": prediction.get('trend', 'stable')
    }

    # Get response in English
    response = chatbot.get_response(message, enriched_data)

    # Translate if needed
    translated_response = response
    if lang != 'en':
        try:
            from deep_translator import GoogleTranslator
            translated_response = GoogleTranslator(source='auto', target=lang).translate(response)
        except Exception:
            translated_response = response

    return jsonify({
        "response": translated_response,
        "original": response,
        "lang": lang
    })


@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text to target language."""
    data = json_payload()
    text = str(data.get('text', ''))
    target_lang = normalize_lang(data.get('target', DEFAULT_LANG))

    if not text.strip():
        return jsonify({"error": "Empty text"}), 400

    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return jsonify({
            "translated": result,
            "original": text,
            "source_lang": "auto",
            "target_lang": target_lang
        })
    except Exception as e:
        return jsonify({
            "translated": text,
            "error": str(e)
        })


@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Generate speech audio from text using gTTS."""
    data = json_payload()
    text = str(data.get('text', ''))
    lang = normalize_lang(data.get('lang', DEFAULT_LANG))

    # Map our language codes to gTTS codes
    lang_map = {'en': 'en', 'te': 'te', 'hi': 'hi', 'ta': 'ta'}
    gtts_lang = lang_map.get(lang, 'en')

    if not text.strip():
        return jsonify({"error": "Empty text"}), 400

    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout the user."""
    session.clear()
    return jsonify({"success": True})


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', port=int(os.environ.get('PORT', 5000)))
