from flask import Flask, redirect, send_from_directory, render_template
app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return send_from_directory("./","animation.mp4")

# app.run()

@app.route('/')
def index():
    return render_template('index.html')

app.run()