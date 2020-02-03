# source venv/bin/activate
# pip install python-dotenv
# pip install -r requirements.txt
# flask run
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap


from textblob import TextBlob, Word
import random

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['POST'])
def analyse():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        blob = TextBlob(rawtext)
        blob_sentiment, blob_subjectivity = blob.sentiment.polarity, blob.subjectivity
        tokens = [blob.words]

    return render_template('index.html', received_text = blob, tokens=tokens, blob_sentiment = blob_sentiment,
                           blob_subjectivity = blob_subjectivity)

if __name__ == '__main__':
    app.run(debug=True)
