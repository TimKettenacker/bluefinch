# source venv/bin/activate
# pip install python-dotenv
# pip install -r requirements.txt
# flask run
from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
