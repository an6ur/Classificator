import pandas as pd
import nltk
# nltk.download()
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from pickle import dump, load
from classificator_app.settings import MODEL_PATH

# Create your models here.


class Svc_model:

    def __init__(self, model, vect, transformer):
        self.svclassifier = model
        self.transformer = transformer
        self.vectorizer = vect

    @classmethod
    def prepareText(cls, text: str):
        tokenizer = RegexpTokenizer("\w+")
        words = tokenizer.tokenize(text.lower())
        significant_words = [
            word for word in words if word not in stopwords.words("russian")
        ]
        lemmatizer = WordNetLemmatizer()
        lemms = [lemmatizer.lemmatize(word) for word in significant_words]
        return " ".join(lemms)

    @classmethod
    def createModelFromData(cls, texts: list):
        prepared_texts = [
            {"label": article.label, "text": cls.prepareText(article.text)}
            for article in texts
        ]
        data = pd.DataFrame(prepared_texts, dtype=object)
        count_vect = CountVectorizer()
        counts = count_vect.fit_transform(data["text"])
        transformer = TfidfTransformer().fit(counts)
        counts = transformer.transform(counts)
        model = cls.trainModel(counts, data["label"])
        dump((model, count_vect, transformer), open(MODEL_PATH, "wb"))
        return cls(model, count_vect, transformer)

    @classmethod
    def trainModel(cls, tf_idf: pd.Series, labels: pd.Series):
        X_train, X_test, y_train, y_test = train_test_split(
            tf_idf, labels, test_size=0.3, random_state=69
        )
        svclassifier = SVC(kernel="rbf", С=3)
        svclassifier.fit(X_train, y_train)
        return svclassifier

    @classmethod
    def loadModelFromFile(cls):
        model, vectorizer, transformer = load(open(MODEL_PATH, "rb"))
        return cls(model, vectorizer, transformer)

    def classificateText(self, text: str):
        prepared_text = self.prepareText(text)
        df = pd.DataFrame({"text": [prepared_text]}, dtype=object)
        counts = self.transformer.transform(
            self.vectorizer.transform(df["text"])
        )
        return self.svclassifier.predict(counts)
