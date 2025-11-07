from flask import Flask, render_template, request, flash, send_file

app = Flask(__name__)

@app.route('/')
def index():
    flash('Test message')
    return render_template('index.html', name=request.args.get('name', 'World'))

if __name__ == '__main__':
    app.run()
