"""
Predictive Model for Student Marks Prediction
Uses simple linear regression to predict future semester marks based on historical data.
"""


class PredictiveModel:
    """Predicts future marks based on past semester performance."""

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

        marks = [float(mark) for mark in past_marks]
        semesters = list(range(1, len(marks) + 1))
        x_mean = sum(semesters) / len(semesters)
        y_mean = sum(marks) / len(marks)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(semesters, marks))
        denominator = sum((x - x_mean) ** 2 for x in semesters)
        slope = numerator / denominator if denominator else 0.0
        intercept = y_mean - slope * x_mean

        # Predict next semester
        next_semester = len(marks) + 1
        predicted = intercept + slope * next_semester

        # Clamp between 0 and 100
        predicted = max(0, min(100, round(predicted, 1)))

        # Calculate trend
        trend = "improving" if slope > 0.5 else (
            "declining" if slope < -0.5 else "stable"
        )

        fitted_marks = [intercept + slope * x for x in semesters]
        total_error = sum((y - y_mean) ** 2 for y in marks)
        residual_error = sum((y - fitted) ** 2 for y, fitted in zip(marks, fitted_marks))
        r2 = 1.0 if total_error == 0 else 1 - (residual_error / total_error)
        confidence = max(0, min(100, round(r2 * 100, 1)))

        return {
            "predicted_mark": predicted,
            "trend": trend,
            "confidence": confidence,
            "next_semester": next_semester,
            "slope": round(slope, 2)
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
