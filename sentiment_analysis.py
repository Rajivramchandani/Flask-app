import pickle
from keras.models import model_from_json
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from numpy.lib.function_base import average
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('wordnet')


def clean_data(text):
    text = re.sub(r'[^\ a-zA-Z0-9]+', '', text)  # Removes non alphanumeric
    # Removes extra whitespace, tabs
    text = re.sub(r'^\s*|\s\s*', ' ', text).strip()
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    text = text.lower().split()  # Converts text to lowercase
    cleaned_text = list()
    for word in text:
        if word in stop_words:  # Removes Stopwords, i.e words that don't convey any meaningful context/sentiments
            continue
        # Lemmatize words, pos = verbs, i.e playing, played becomes play
        word = lemmatizer.lemmatize(word, pos='v')
        cleaned_text.append(word)
    text = ' '.join(cleaned_text)
    return text


def load_model():
    # load json and create model
    json_file = open('static/model/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("static/model/model.h5")
    # loading
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    return loaded_model, tokenizer


def get_sentiment(filename):
    df = pd.read_csv(f'outputs/{filename}.csv')
    df['cleaned_tweet'] = df['Text'].apply(lambda x: clean_data(x))
    # df.Timestamp = pd.to_datetime(df['Timestamp']).dt.strftime('%d/%m/%Y')
    loaded_model, tokenizer = load_model()
    arr = {}
    sentiment_score = 0
    result = ''
    for index, row in df.iterrows():
        tokens = tokenizer.texts_to_sequences([row['Text']])
        tokens = pad_sequences(tokens, maxlen=280)
        sentiment = loaded_model.predict(
            np.array(tokens), batch_size=1, verbose=2)[0][0]
        arr[row['Timestamp']] = sentiment
        print(sentiment)
        sentiment_score = (sentiment+sentiment_score)/2
    if (round(sentiment_score) == 0):
        result = 'Negative'
    else:
        result = 'Positive'

    # Plot the average score per day
    d = pd.DataFrame(list(arr.items()), columns=['Timestamp', 'score'])
    d.Timestamp = pd.to_datetime(d['Timestamp']).dt.strftime('%d/%m/%Y')
    group = d.groupby(d.Timestamp)
    plt.figure(figsize=(10, 10))
    group.score.mean().plot.barh()
    plt.xticks(rotation=0)
    plt.style.use("dark_background")
    plt.savefig(f'static/images/{filename}_score_graph.png',
                bbox_inches='tight', pad_inches=0.5)
    plt.close()
    return sentiment_score, result


# get_sentiment('outputs/spicy.csv')

# print(clean_data("Trying out the #ghostpepper chips! With my lil sis! Full video in the link https://youtu.be/CNN_etVepgQ. #YouTuber #FortniteSeason6 #Fortnite #Memes #Hot #Spicy #SmallStreamerCommunity #smallstreamers #subscribers #Like #ContentCreator #fypシ #siblinggoals #gamer #pcgaming #twitchtv"))
