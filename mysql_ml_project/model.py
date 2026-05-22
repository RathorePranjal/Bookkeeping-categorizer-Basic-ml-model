import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle

# Train and save model
def train_model():
    data = pd.read_csv('sample_data.csv')
    X = data['text']
    y = data['label']

    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', MultinomialNB())
    ])

    model.fit(X, y)

    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

    print("✓ Model trained and saved as model.pkl")

# Test prediction
def predict_label(text):
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model.predict([text])[0]

if __name__ == "__main__":
    # Train the model
    train_model()

    # Test it
    test_text = input("Enter a transaction to test: ")
    predicted = predict_label(test_text)
    print(f"Predicted label: {predicted}")