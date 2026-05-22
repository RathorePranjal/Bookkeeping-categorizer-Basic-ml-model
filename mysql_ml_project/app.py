from flask import Flask, request, render_template_string, jsonify
import pickle
import mysql.connector
from config import MYSQL_CONFIG

app = Flask(__name__)

# Database helper
def db_execute(query, params=None, fetch=False):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    result = cursor.fetchall() if fetch else None
    conn.commit()
    cursor.close()
    conn.close()
    return result

# Predict function
def predict(text):
    with open('model.pkl', 'rb') as f:
        return pickle.load(f).predict([text])[0]

# Routes
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/predict', methods=['POST'])
def classify():
    text = request.json['text']
    label = predict(text)
    db_execute("INSERT INTO predictions (text, predicted_label) VALUES (%s, %s)", (text, label))
    return jsonify({'label': label, 'message': f'{text} → {label}'})

@app.route('/predictions')
def get_predictions():
    rows = db_execute("SELECT id, text, predicted_label FROM predictions ORDER BY id DESC", fetch=True)
    return jsonify([{'id': r[0], 'text': r[1], 'label': r[2]} for r in rows])

@app.route('/clear', methods=['DELETE'])
def clear():
    db_execute("DELETE FROM predictions")
    db_execute("ALTER TABLE predictions AUTO_INCREMENT = 1")
    return jsonify({'success': True})

# HTML Template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Accounting Classifier</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; background: #f4f4f4; padding: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1 { text-align: center; color: #333; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #45a049; }
        .delete-btn { background: #f44336; float: right; }
        .delete-btn:hover { background: #da190b; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background: #4CAF50; color: white; padding: 10px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f5f5f5; }
        #result { padding: 15px; background: #e7f3e7; border-radius: 4px; margin-top: 10px; display: none; }
        .header { display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <h1>Smart Accounting Classifier</h1>
    
    <div class="card">
        <input id="text" placeholder="e.g., sold finished goods 15000" />
        <button onclick="classify()">Classify</button>
        <div id="result"></div>
    </div>

    <div class="card">
        <div class="header">
            <h2 style="margin:0">History</h2>
            <button class="delete-btn" onclick="clearHistory()">Clear All</button>
        </div>
        <table id="table">
            <thead><tr><th>ID</th><th>Text</th><th>Label</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>

    <script>
        function loadHistory() {
            fetch('/predictions')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.querySelector('#table tbody');
                    tbody.innerHTML = data.length ? 
                        data.map(p => `<tr><td>${p.id}</td><td>${p.text}</td><td><b>${p.label}</b></td></tr>`).join('') :
                        '<tr><td colspan="3" style="text-align:center">No predictions yet</td></tr>';
                });
        }

        function classify() {
            const text = document.getElementById('text').value;
            const result = document.getElementById('result');
            
            fetch('/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text})
            })
            .then(r => r.json())
            .then(data => {
                result.style.display = 'block';
                result.innerHTML = `<b>Label:</b> ${data.label}`;
                document.getElementById('text').value = '';
                loadHistory();
            });
        }

        function clearHistory() {
            if (confirm('Delete all history? This cannot be undone!')) {
                fetch('/clear', {method: 'DELETE'})
                    .then(r => r.json())
                    .then(() => loadHistory());
            }
        }

        window.onload = loadHistory;
        document.getElementById('text').addEventListener('keypress', e => {
            if (e.key === 'Enter') classify();
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)