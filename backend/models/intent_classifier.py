import re
from typing import Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Training dataset for Intent Classifier
INTENT_TRAINING_DATA = [
    ("change department of student to ai", "UPDATE"),
    ("update the salary of employee to 50000", "UPDATE"),
    ("change phone number of ravi to 9876543210", "UPDATE"),
    ("modify grade of student 102 to A", "UPDATE"),
    ("set price of product P100 to 250", "UPDATE"),
    ("replace email of john with john@example.com", "UPDATE"),
    ("add new student 1031 with name John", "ADD"),
    ("insert row for employee E108", "ADD"),
    ("add column address to dataset", "ADD"),
    ("insert new column rating", "ADD"),
    ("create column bonus", "ADD"),
    ("add new record for user 1050", "ADD"),
    ("delete student record 1025", "DELETE"),
    ("remove record for employee E104", "DELETE"),
    ("delete column phone", "DELETE"),
    ("remove phone column", "DELETE"),
    ("drop column gpa", "DELETE"),
    ("erase row 5", "DELETE"),
    ("delete row for student 1022", "DELETE"),
    ("find the employee with id E105", "FIND"),
    ("search student record 1025", "FIND"),
    ("locate details of customer C400", "FIND"),
    ("show row for student 101", "FIND"),
    ("analyze the sales data", "ANALYZE"),
    ("show stats and distribution", "ANALYZE"),
    ("generate correlation matrix and overview", "ANALYZE"),
    ("evaluate dataset metrics", "ANALYZE"),
    ("clean the customer data", "CLEAN"),
    ("remove missing values and duplicates", "CLEAN"),
    ("fix outliers and extra spaces", "CLEAN"),
    ("sanitize missing entries", "CLEAN"),
    ("predict next month sales", "PREDICT"),
    ("forecast price of house", "PREDICT"),
    ("train model to predict outcome", "PREDICT"),
    ("run classification prediction", "PREDICT"),
]

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.model = MultinomialNB()
        self._train()
        
    def _train(self):
        texts = [text for text, intent in INTENT_TRAINING_DATA]
        labels = [intent for text, intent in INTENT_TRAINING_DATA]
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Returns (intent, confidence_score)
        Intents: UPDATE, ADD, DELETE, FIND, ANALYZE, CLEAN, PREDICT
        """
        text_clean = text.lower().strip()
        
        # Rule-based overrides for high confidence
        if any(w in text_clean for w in ["add", "insert", "append", "create column"]):
            return "ADD", 0.95
        elif any(w in text_clean for w in ["delete", "remove record", "remove row", "remove column", "drop column", "erase"]):
            return "DELETE", 0.95
        elif any(w in text_clean for w in ["change", "update", "modify", "set", "replace"]):
            return "UPDATE", 0.95
        elif any(w in text_clean for w in ["find", "search", "locate", "lookup"]):
            return "FIND", 0.92
        elif any(w in text_clean for w in ["clean", "remove duplicates", "fix missing", "sanitize"]):
            return "CLEAN", 0.93
        elif any(w in text_clean for w in ["predict", "forecast", "estimate"]):
            return "PREDICT", 0.94
        elif any(w in text_clean for w in ["analyze", "stats", "correlation", "overview"]):
            return "ANALYZE", 0.91
            
        # ML Model Fallback
        vec = self.vectorizer.transform([text_clean])
        probs = self.model.predict_proba(vec)[0]
        max_idx = probs.argmax()
        intent = self.model.classes_[max_idx]
        confidence = float(probs[max_idx])
        return intent, round(max(confidence, 0.70), 2)

intent_classifier_instance = IntentClassifier()
