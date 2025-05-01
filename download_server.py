from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Cinderella Bot Download</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f8ff;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background-color: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    max-width: 600px;
                }
                h1 {
                    color: #4a0080;
                    margin-bottom: 20px;
                }
                p {
                    color: #333;
                    line-height: 1.6;
                    margin-bottom: 25px;
                }
                .download-button {
                    background-color: #4a0080;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    text-decoration: none;
                    transition: background-color 0.3s;
                }
                .download-button:hover {
                    background-color: #7b00d3;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Cinderella Bot Download</h1>
                <p>Click the button below to download the Cinderella Bot package with enhanced voice chat capabilities.</p>
                <a href="/download" class="download-button">Download Cinderella Bot</a>
            </div>
        </body>
    </html>
    '''

@app.route('/download')
def download():
    zip_path = os.path.join(os.getcwd(), 'cinderella_bot.zip')
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)