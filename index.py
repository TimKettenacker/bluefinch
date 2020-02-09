# source venv/bin/activate
# pip install python-dotenv
# pip install -r requirements.txt
# flask run
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

app = Flask(__name__)
Bootstrap(app)

bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
trainer = ChatterBotCorpusTrainer(bot)
trainer.train("chatterbot.corpus.german.conversations", "chatterbot.corpus.german.greetings")

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(bot.get_response(userText))


if __name__ == '__main__':
    app.run(debug=True)
