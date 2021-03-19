from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from Scweet.scweet import scrap
import pandas as pd



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('my-form.html')


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



@app.route('/compute')
def compute():
    topic = request.args.get('topic')
    hashtag =  request.args.get('hashtag')
    startdate =  request.args.get('startdate')
    enddate =  request.args.get('enddate')
    
    print(topic,hashtag,startdate,enddate)
    data = scrap(words=topic ,hashtag=hashtag, start_date=startdate, max_date=enddate ,from_account = None,interval=1,
                 headless=True, display_type="Top", save_images=False, resume=False, filter_replies=True, proximity=False,)
    
    # users = ['nagouzil', '@yassineaitjeddi', 'TahaAlamIdrissi', 
    #         '@Nabila_Gl', 'geceeekusuu', '@pabu232', '@av_ahmet', '@x_born_to_die_x']

    # users_info = get_user_information(users, headless=True)
      
    return render_template('dataframe.html',  tables=[data.to_html(classes='data')], titles=data.columns.values)


