#!/usr/bin/env python3
# in cmd: navigate to project directory
# source venv/bin/activate
# pip install python-dotenv
# pip install -r requirements.txt
# python -m spacy download de_core_news_sm
# flask run
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap
from chatbot import Chatbot

app = Flask(__name__)
Bootstrap(app)

bot = Chatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(bot.respond_user(input=userText))

if __name__ == '__main__':
    app.run(debug=True)
