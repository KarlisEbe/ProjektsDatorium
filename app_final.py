from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import os
import zipfile
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
ARCHIVE_FOLDER = 'archives'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ARCHIVE_FOLDER'] = ARCHIVE_FOLDER


for folder in [UPLOAD_FOLDER, STATIC_FOLDER, ARCHIVE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

data_df = pd.DataFrame()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fitnesa Progresa Sekotājs</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            text-align: center;
            background-color: #e0f7fa;
            padding: 40px;
            transition: background-color 0.5s;
            overflow-x: hidden;
            animation: fadeIn 0.8s ease-out;
        }
        h1 {
            color: #00796b;
            animation: slideDown 0.8s ease-out;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        form {
            margin-top: 20px;
            animation: fadeIn 1s ease-out;
        }
        input[type="file"] {
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            border: 2px dashed #00796b;
            background-color: rgba(255,255,255,0.7);
            transition: all 0.4s ease;
            animation: pulse 2s infinite;
        }
        input[type="file"]:hover {
            background-color: rgba(255,255,255,0.9);
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,121,107,0.3);
        }
        .button {
            background-color: #00796b;
            color: white;
            border: none;
            padding: 12px 25px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: fadeIn 1.2s ease-out;
        }
        .button:hover {
            background-color: #004d40;
            transform: translateY(-3px);
            box-shadow: 0 7px 14px rgba(0,0,0,0.2);
        }
        .button:active {
            transform: translateY(1px);
        }
        img {
            max-width: 80%;
            height: auto;
            margin: 25px 0;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
            cursor: zoom-in;
        }
        img:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        #statistics {
            margin: 30px auto;
            padding: 20px;
            border: 1px solid #4db6ac;
            border-radius: 10px;
            background-color: #e0f2f1;
            text-align: left;
            max-width: 500px;
            box-shadow: 0 4px 8px rgba(77,182,172,0.2);
            animation: fadeInUp 1s ease-out;
        }
        .copy-button {
            background-color: #4db6ac;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 5px;
            margin-left: 10px;
            transition: all 0.3s;
        }
        .copy-button:hover {
            background-color: #26a69a;
            transform: scale(1.05);
        }
        p {
            animation: fadeIn 1s ease-out;
            line-height: 1.6;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideDown {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes fadeInUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 rgba(0,121,107,0.4); }
            70% { transform: scale(1.01); box-shadow: 0 0 10px rgba(0,121,107,0.4); }
            100% { transform: scale(1); box-shadow: 0 0 0 rgba(0,121,107,0.4); }
        }
        .floating {
            animation: floating 3s ease-in-out infinite;
        }
        @keyframes floating {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        .success-message {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            animation: fadeInOut 3s ease-in-out;
            display: none;
        }
        @keyframes fadeInOut {
            0% { opacity: 0; }
            20% { opacity: 1; }
            80% { opacity: 1; }
            100% { opacity: 0; }
        }
    </style>
</head>
<body>
    <h1 class="floating">Fitnesa Progresa Sekotājs</h1>
    
    {% if not chart %}
        <p>Laipni lūdzam Fitnesa Progresa Sekotājā! Augšupielādējiet savu CSV failu, lai vizualizētu savus treniņu datus un sekotu līdzi savam progresam.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br>
            <input type="submit" class="button" value="Augšupielādēt">
        </form>
    {% else %}
        <div id="success-message" class="success-message">Dati veiksmīgi augšupielādēti!</div>
        
        <h2>Progresijas grafiks</h2>
        <img src="{{ url_for('static', filename='progress.png') }}" alt="Progresijas grafiks" onclick="zoomImage(this)">
        <form action="/download/graph/progress" method="get">
            <input type="submit" class="button" value="Lejupielādēt PNG">
        </form>

        <h2>Treniņu biežums</h2>
        <img src="{{ url_for('static', filename='frequency.png') }}" alt="Biežums" onclick="zoomImage(this)">
        <form action="/download/graph/frequency" method="get">
            <input type="submit" class="button" value="Lejupielādēt PNG">
        </form>

        <h2>Sirdsdarbības izmaiņas</h2>
        <img src="{{ url_for('static', filename='heartrate.png') }}" alt="Pulss" onclick="zoomImage(this)">
        <form action="/download/graph/heartrate" method="get">
            <input type="submit" class="button" value="Lejupielādēt PNG">
        </form>
        
        <div id="statistics">
            <h3>Statistika</h3>
            <p>Vidējais paceltais svars: {{ avg_weight }} kg</p>
            <p>Treniņu skaits: {{ workout_count }}</p>
            <p>Vidējais sirdsdarbības ātrums: {{ avg_heartrate }} bpm</p>
        </div>
        
        <div class="link"><a href="/" class="button">Augšupielādēt citu failu</a></div>
    {% endif %}
    
    <script>
        function zoomImage(img) {
            const newWindow = window.open("");
            newWindow.document.write('<html><head><title>Zoomed Image</title><style>body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; } img { max-width: 90%; max-height: 90%; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }</style></head><body>');
            newWindow.document.write('<img src="' + img.src + '">');
            newWindow.document.write('</body></html>');
            newWindow.document.close();
        }

        // Parādām veiksmīgas augšupielādes ziņojumu
        document.addEventListener('DOMContentLoaded', function() {
            if (document.getElementById('success-message')) {
                const msg = document.getElementById('success-message');
                msg.style.display = 'block';
                setTimeout(() => {
                    msg.style.display = 'none';
                }, 3000);
            }
        });
    </script>
</body>
</html>
"""

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, chart=False)

@app.route('/upload', methods=['POST'])
def upload():
    global data_df
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            data_df = pd.read_csv(filepath)
        except Exception as e:
            return f"Kļūda nolasot CSV failu: {e}"

        required_cols = {'Date', 'Exercise', 'Weight', 'Reps', 'HeartRate'}
        if not required_cols.issubset(set(data_df.columns)):
            return f"CSV failā jābūt kolonnām: {required_cols}"

        
        data_df['Date'] = pd.to_datetime(data_df['Date'], errors='coerce')
        data_df.dropna(subset=['Date'], inplace=True)

        
        avg_weight = round(data_df['Weight'].mean(), 2)
        workout_count = data_df['Date'].nunique()
        avg_heartrate = round(data_df['HeartRate'].mean(), 1)

        
        draw_graphs(data_df)

        return render_template_string(HTML_TEMPLATE, chart=True, 
                                   avg_weight=avg_weight, 
                                   workout_count=workout_count, 
                                   avg_heartrate=avg_heartrate)
    else:
        return "Lūdzu augšupielādē derīgu .csv failu!"

def draw_graphs(df):
    
    prog = df.groupby('Date')['Weight'].mean()
    plt.figure(figsize=(12, 6))
    prog.plot(marker='o', color='green', linewidth=2, markersize=8)
    plt.title('Vidējais paceltais svars', fontsize=14, pad=20)
    plt.xlabel('Datums', fontsize=12)
    plt.ylabel('Svars (kg)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_FOLDER, 'progress.png'), dpi=100)
    plt.close()

    
    freq = df['Date'].dt.date.value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    freq.plot(kind='bar', color='blue', width=0.8)
    plt.title('Treniņu biežums', fontsize=14, pad=20)
    plt.xlabel('Datums', fontsize=12)
    plt.ylabel('Treniņu skaits', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_FOLDER, 'frequency.png'), dpi=100)
    plt.close()

   
    hr = df.groupby('Date')['HeartRate'].mean()
    plt.figure(figsize=(12, 6))
    hr.plot(marker='x', color='red', linewidth=2, markersize=8)
    plt.title('Vidējais sirdsdarbības ātrums', fontsize=14, pad=20)
    plt.xlabel('Datums', fontsize=12)
    plt.ylabel('Sirdsdarbības ātrums (bpm)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_FOLDER, 'heartrate.png'), dpi=100)
    plt.close()

@app.route('/download/graph/<graph_type>', methods=['GET'])
def download_graph(graph_type):
    graph_files = {
        'progress': 'progress.png',
        'frequency': 'frequency.png',
        'heartrate': 'heartrate.png'
    }
    if graph_type in graph_files:
        return send_from_directory(STATIC_FOLDER, graph_files[graph_type], as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)