from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/api/highscores')
def get_highscores():
    # Mock high scores data
    return jsonify([
        {"name": "ACE", "score": 125000},
        {"name": "PWR", "score": 98750},
        {"name": "MAX", "score": 87500},
        {"name": "ZAP", "score": 76250},
        {"name": "GUN", "score": 65000}
    ])

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "service": "bolamiga"})

@app.route('/minimal')
def minimal_game():
    return render_template('minimal-game.html')

if __name__ == '__main__':
    # Port management
    port = int(os.environ.get('PORT', 5030))
    print("Starting RetroBlaster on port {}".format(port))
    print("Access game at: http://localhost:{}".format(port))
    
    app.run(debug=True, host='0.0.0.0', port=port)