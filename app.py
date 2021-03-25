from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import wordcloud
from Scweet.scweet import scrap
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from  sentiment_analysis import get_sentiment
plt.style.use("dark_background")


#Define Wordcloud method
def word_cloud(wd_list,filename):
    stopwords = set(STOPWORDS)
    all_words = ' '.join([text for text in wd_list])
    wordcloud = WordCloud(
        background_color='black',
        stopwords=stopwords,
        width=1600,
        height=800,
        random_state=1,
        colormap='jet',
        max_words=80,
        max_font_size=200).generate(all_words)
    plt.figure(figsize=(12, 10))
    plt.axis('off')
    plt.imshow(wordcloud, interpolation="bilinear");
    plt.savefig(f'static/images/{filename}_wordcloud.png', bbox_inches = 'tight', pad_inches = 0)
    plt.close()

# Show number of tweets per day
def tweet_daily(dataset,filename):
    dataset.Timestamp = pd.to_datetime(dataset['Timestamp']).dt.strftime('%d/%m/%Y')
    group = dataset.groupby(dataset.Timestamp)
    plt.figure(figsize=(10,10))
    group.Text.size().plot.barh()
    plt.xticks(rotation=0)
    plt.savefig(f'static/images/{filename}_tweet_daily.png', bbox_inches = 'tight', pad_inches = 0.5)
    plt.close()



app = Flask(__name__)

# initial route
@app.route('/')
def index():
    return render_template('my-form.html')

# Return suggessions from google suggesions api
@app.route('/suggestions')
def suggestions():
    text = request.args.get('jsdata')
    
    print(text)

    suggestions_list = []

    if text:
        r = requests.get('http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q={}&gl=in'.format(text))
        
        soup = BeautifulSoup(r.content, 'lxml')

        suggestions = soup.find_all('suggestion')

        for suggestion in suggestions:
            suggestions_list.append(suggestion.attrs['data'])

        # print(suggestions_list)

    return render_template('suggestions.html', suggestions=suggestions_list)


# scraping function and plot wordcloud and number of tweets per day
@app.route('/scrape_data')
def scrape_data():
    topic = request.args.get('topic')
    hashtag =  request.args.get('hashtag')
    startdate =  request.args.get('startdate')
    enddate =  request.args.get('enddate')
    filename = f'{topic}_{startdate}_{enddate}'
    
    print(topic,hashtag,startdate,enddate)
    data = scrap(words=topic ,hashtag=hashtag, start_date=startdate, max_date=enddate ,from_account = None,interval=1,
                 headless=True, display_type="Top", save_images=False, resume=False, filter_replies=True, proximity=False,lang='en')
    
    # users = ['nagouzil', '@yassineaitjeddi', 'TahaAlamIdrissi', 
    #         '@Nabila_Gl', 'geceeekusuu', '@pabu232', '@av_ahmet', '@x_born_to_die_x']

    # users_info = get_user_information(users, headless=True)
    word_cloud(data.Text,filename)
    tweet_daily(data,filename)
    sample = data.head().drop(columns=['UserScreenName','Embedded_text','Tweet URL','Image link'],)
    sample.Timestamp = pd.to_datetime(sample['Timestamp']).dt.strftime('%d/%m/%Y')

    #  to preserve memory remove data
    data = None
    return render_template('dataframe.html',  tables=[sample.to_html(classes='data',index = False)] ,wordcloud = f'static/images/{filename}_wordcloud.png', tweet_daily=f'static/images/{filename}_tweet_daily.png')

# get sentiment analysis results from sentiment_analysis.py
@app.route('/sentiment_analysis')
def sentiment_analysis():

    file_name = request.args.get('filename')
    print(file_name)

    sentiment_score,result = get_sentiment(file_name)
    print(sentiment_score,result)
    
    return render_template('sentiment_analysis.html', score = sentiment_score, result=result, score_graph= f'static/images/{file_name}_score_graph.png')