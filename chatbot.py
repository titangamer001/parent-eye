"""
Multilingual Chatbot for Parent Eye
Handles parent queries about student performance, attendance, marks, etc.
Responds in English and translates to the requested language.
"""

import random


# Knowledge base with intent patterns and responses
KNOWLEDGE_BASE = {
    "greeting": {
        "patterns": ["hello", "hi", "hey", "good morning", "good evening", "namaste", "vanakkam"],
        "responses": [
            "Hello! Welcome to Parent Eye. How can I help you today?",
            "Hi there! I'm here to help you with your child's academic information.",
            "Welcome! Ask me anything about your child's performance."
        ]
    },
    "marks": {
        "patterns": ["marks", "score", "grades", "result", "exam", "test", "percentage", "mark"],
        "responses": [
            "Your child's latest marks are displayed on the dashboard. Overall average is {avg_marks}%. The strongest subject is {best_subject} with {best_marks}%.",
            "Based on the recent exams, your child scored an average of {avg_marks}%. They performed best in {best_subject} ({best_marks}%).",
            "Here's a summary: Average marks = {avg_marks}%, Best subject = {best_subject} ({best_marks}%), Area to improve = {worst_subject} ({worst_marks}%)."
        ]
    },
    "attendance": {
        "patterns": ["attendance", "absent", "present", "leave", "absent days", "coming to school"],
        "responses": [
            "Your child's attendance this semester is {attendance}%. Regular attendance is important for academic success.",
            "Current attendance stands at {attendance}%. {attendance_msg}",
            "Attendance record: {attendance}% this semester. {attendance_msg}"
        ]
    },
    "prediction": {
        "patterns": ["predict", "future", "next exam", "next semester", "expected", "will score", "upcoming"],
        "responses": [
            "Based on the trend analysis, your child is predicted to score around {predicted}% in the next semester. The performance trend is {trend}.",
            "Our AI model predicts approximately {predicted}% for the next assessment. The trend shows {trend} performance.",
            "Prediction for next semester: {predicted}%. Current trend: {trend}. Keep encouraging your child!"
        ]
    },
    "improvement": {
        "patterns": ["improve", "better", "help", "weak", "poor", "low marks", "fail", "struggling"],
        "responses": [
            "To improve performance, focus on {worst_subject} where marks are {worst_marks}%. Regular practice and revision can help significantly.",
            "I suggest extra attention on {worst_subject} ({worst_marks}%). Setting a daily study schedule and practicing problems can make a big difference.",
            "{worst_subject} needs improvement ({worst_marks}%). Consider extra tutoring or practice sessions. The school also offers remedial classes."
        ]
    },
    "teacher": {
        "patterns": ["teacher", "contact", "meet", "parent meeting", "pta", "class teacher"],
        "responses": [
            "You can contact the class teacher through the school office. Parent-teacher meetings are held on the first Saturday of every month.",
            "To schedule a meeting with the teacher, please call the school office at the number provided in the dashboard notifications.",
            "Parent-Teacher meetings are scheduled monthly. Check the dashboard for upcoming dates and teacher contact information."
        ]
    },
    "schedule": {
        "patterns": ["schedule", "timetable", "exam date", "holiday", "vacation", "when"],
        "responses": [
            "The exam schedule and academic calendar are available on the dashboard. Next exams are expected in March.",
            "Please check the dashboard for the latest timetable and exam schedule updates.",
            "Academic schedule details are updated regularly on the dashboard. Check the notifications section for any changes."
        ]
    },
    "farewell": {
        "patterns": ["bye", "goodbye", "thank", "thanks", "see you", "quit", "exit"],
        "responses": [
            "Thank you for using Parent Eye! Feel free to come back anytime.",
            "Goodbye! Wishing your child the best in their studies.",
            "You're welcome! Don't hesitate to ask if you need anything else."
        ]
    }
}


class Chatbot:
    """Multilingual chatbot for parent queries about student performance."""

    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE

    def get_intent(self, message):
        """Identify the intent of the user message."""
        message_lower = message.lower().strip()
        best_intent = None
        best_score = 0

        for intent, data in self.knowledge_base.items():
            for pattern in data["patterns"]:
                if pattern in message_lower:
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_intent = intent

        return best_intent or "default"

    def get_response(self, message, student_data=None):
        """
        Generate a response based on the message and student data.

        Args:
            message: user's question/message string
            student_data: dict with student performance data

        Returns:
            response string in English
        """
        intent = self.get_intent(message)

        if intent == "default":
            return "I can help you with information about your child's marks, attendance, predictions, and more. Please ask about any of these topics!"

        responses = self.knowledge_base[intent]["responses"]
        response = random.choice(responses)

        # Fill in dynamic data if available
        if student_data:
            try:
                marks = student_data.get("marks", {})
                if marks:
                    avg_marks = round(sum(marks.values()) / len(marks), 1)
                    best_subject = max(marks, key=marks.get)
                    best_marks = marks[best_subject]
                    worst_subject = min(marks, key=marks.get)
                    worst_marks = marks[worst_subject]
                else:
                    avg_marks = best_marks = worst_marks = 0
                    best_subject = worst_subject = "N/A"

                attendance = student_data.get("attendance", 85)
                attendance_msg = "Great attendance!" if attendance >= 85 else "Attendance needs improvement. Please ensure regular attendance."

                predicted = student_data.get("predicted_mark", avg_marks + 2)
                trend = student_data.get("trend", "stable")

                response = response.format(
                    avg_marks=avg_marks,
                    best_subject=best_subject,
                    best_marks=best_marks,
                    worst_subject=worst_subject,
                    worst_marks=worst_marks,
                    attendance=attendance,
                    attendance_msg=attendance_msg,
                    predicted=predicted,
                    trend=trend
                )
            except (KeyError, ValueError):
                pass

        return response


# Singleton instance
chatbot = Chatbot()
