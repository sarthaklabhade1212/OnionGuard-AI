import os
import joblib
import numpy as np

class SpoilagePredictor:
    """
    Wrapper for spoilage prediction.
    If a trained model (model.pkl) exists it uses it.
    Otherwise it falls back to a rule-based heuristic.
    Prediction returned as {'risk': 'Low'|'Medium'|'High',
                           'probability': 0.0-1.0,
                           'method': 'model'|'rule'}
    """
    def __init__(self, model_path="model/model.pkl"):
        self.model_path = model_path
        self.model = None
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception:
                self.model = None

    def predict_single(self, temperature, humidity, gas):
        x = np.array([[temperature, humidity, gas]])
        if self.model is not None:
            try:
                prob = float(self.model.predict_proba(x)[0][1])  # binary prob for class 1
                risk = self._prob_to_risk(prob)
                return {"risk": risk, "probability": round(prob, 3), "method": "model"}
            except Exception:
                pass

        # Rule-based fallback
        prob = self._rule_probability(temperature, humidity, gas)
        risk = self._prob_to_risk(prob)
        return {"risk": risk, "probability": round(prob, 3), "method": "rule"}

    def _rule_probability(self, t, h, g):
        # heuristic scoring: humidity and gas are major contributors
        score = 0.0
        # humidity: ideal 60-70
        if h < 50: score += 0.1
        elif 50 <= h <= 70: score += 0.0
        elif 70 < h <= 80: score += 0.3
        else: score += 0.6

        # temperature: ideal 20-25
        if t < 10: score += 0.1
        elif 10 <= t <= 25: score += 0.0
        elif 25 < t <= 30: score += 0.2
        else: score += 0.5

        # gas: raw value heuristic (tune for MQ-135)
        if g < 200: score += 0.0
        elif 200 <= g <= 400: score += 0.2
        elif 400 < g <= 800: score += 0.4
        else: score += 0.7

        # normalize to 0..1 roughly
        prob = max(0.0, min(1.0, score / 1.6))
        return prob

    def _prob_to_risk(self, p):
        if p < 0.25:
            return "Low"
        elif p < 0.6:
            return "Medium"
        else:
            return "High"
