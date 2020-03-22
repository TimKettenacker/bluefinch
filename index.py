# source venv/bin/activate
# pip install python-dotenv
# pip install -r requirements.txt
# python -m spacy download de_core_news_sm
# flask run
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from CustomTrainer import CustomTrainer


app = Flask(__name__)
Bootstrap(app)

bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter",
                logic_adapters=[
                        {
                            'import_path': 'chatterbot.logic.BestMatch',
                            'default_response': 'Entschuldigung, das habe ich nicht ganz verstanden.',
                            'maximum_similarity_threshold': 0.90
                        }
                    ]
              )
trainer = ChatterBotCorpusTrainer(bot)
trainer.train("chatterbot.corpus.german.conversations", "chatterbot.corpus.german.greetings")
#trainer = CustomTrainer(bot)
#trainer.train("chatterbot.corpus.german.conversations", "chatterbot.corpus.german.greetings")

@app.route('/')
def index():
    # for future implementation: on startup, load the ontology in the background
    return render_template('index.html')


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    # parse input from the user (Natural Language Understanding)
    # https://explosion.ai/blog/german-model
    # https://github.com/adbar/German-NLP#Text-corpora
    return str(bot.get_response(userText))


if __name__ == '__main__':
    app.run(debug=True)


