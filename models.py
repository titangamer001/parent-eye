"""
Predictive Model for Student Marks Prediction
Uses Linear Regression to predict future semester marks based on historical data.
"""

import numpy as np
from sklearn.linear_model import LinearRegression


class PredictiveModel:
    """Predicts future marks based on past semester performance."""

    def __init__(self):
        self.model = LinearRegression()

    def predict_future_marks(self, past_marks):
        """
        Given a list of past marks (e.g., [75, 78, 82, 80]),
        predicts the next semester's mark.

        Args:
            past_marks: list of integers/floats representing marks in chronological order

        Returns:
            dict with predicted mark and confidence info
        """
        if not past_marks or len(past_marks) < 2:
            return {
                "predicted_mark": None,
                "error": "Need at least 2 past marks to make a prediction"
            }

        # Prepare data: X = semester numbers, y = marks
        semesters = np.array(range(1, len(past_marks) + 1)).reshape(-1, 1)
        marks = np.array(past_marks)

        # Train model
        self.model.fit(semesters, marks)

        # Predict next semester
        next_semester = np.array([[len(past_marks) + 1]])
        predicted = self.model.predict(next_semester)[0]

        # Clamp between 0 and 100
        predicted = max(0, min(100, round(predicted, 1)))

        # Calculate trend
        trend = "improving" if self.model.coef_[0] > 0.5 else (
            "declining" if self.model.coef_[0] < -0.5 else "stable"
        )

        # R² score for confidence
        r2 = self.model.score(semesters, marks)

        return {
            "predicted_mark": predicted,
            "trend": trend,
            "confidence": round(r2 * 100, 1),
            "next_semester": len(past_marks) + 1,
            "slope": round(float(self.model.coef_[0]), 2)
        }

    def predict_subject_wise(self, subject_marks_history):
        """
        Predict future marks for each subject.

        Args:
            subject_marks_history: dict like {"Math": [70, 75, 80], "Science": [65, 70, 72]}

        Returns:
            dict of subject -> prediction result
        """
        predictions = {}
        for subject, marks in subject_marks_history.items():
            predictions[subject] = self.predict_future_marks(marks)
        return predictions


# Singleton instance
predictor = PredictiveModel()
