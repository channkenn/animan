import os
from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>画像一覧</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .table-container { display: table; width: 100%; }
        .row { display: table-row; }
        .cell { display: table-cell; padding: 10px; vertical-align: top; border-bottom: 1px solid #ddd; }
        img { max-width: 200px; height: auto; }
        button.copy-btn { margin-left: 10px; padding: 5px 10px; cursor: pointer; }
    </style>
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert("URLをコピーしました: " + text);
            }).catch(err => {
                alert("コピーに失敗しました: " + err);
            });
        }
    </script>
</head>
<body>
    <h1>スレッドから画像を取得</h1>
    <form method="POST" style="margin-bottom: 20px;">
        <label for="url">スレッドのURLを入力してください:</label>
        <input type="text" id="url" name="url" style="width: 400px;" required>
        <button type="submit">画像を取得</button>
    </form>

    {% if thread_url %}
        <div>
            <h2>スレッド情報</h2>
            <p><strong>URL:</strong> <a href="{{ thread_url }}" target="_blank">{{ thread_url }}</a></p>
            <p><strong>タイトル:</strong> {{ thread_title }}</p>
        </div>
    {% endif %}

    {% if images %}
        <h2>取得した画像とソース</h2>
        <div class="table-container">
            {% for image, src in images %}
                <div class="row">
                    <div class="cell">
                        <img src="{{ src }}" alt="Image">
                    </div>
                    <div class="cell">
                        <span>{{ src }}</span>
                        <button class="copy-btn" onclick="copyToClipboard('{{ src }}')">コピー</button>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% endif %}
</body>
</html>
"""

def fetch_images_and_title(thread_url):
    """URLから画像、ソースURL、スレッドタイトルを取得"""
    try:
        response = requests.get(thread_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # スレッドタイトルの取得
        title = soup.title.string if soup.title else "タイトルなし"

        # <img>タグを抽出してリスト化
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                # 完全なURLを構築
                img_url = urljoin(thread_url, src)

                # thumb_mをimgに変換
                if "thumb_m" in img_url:
                    img_url = img_url.replace("/thumb_m/", "/img/")

                images.append((img, img_url))
        return title, images
    except Exception as e:
        return f"<p>エラーが発生しました: {e}</p>", []

@app.route("/", methods=["GET", "POST"])
def index():
    thread_url = None
    thread_title = None
    images = []
    if request.method == "POST":
        # ユーザー入力URL
        thread_url = request.form.get("url")
        if thread_url:
            # スレッドタイトルと画像を取得
            thread_title, images = fetch_images_and_title(thread_url)
    return render_template_string(HTML_TEMPLATE, thread_url=thread_url, thread_title=thread_title, images=images)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 環境変数 PORT を取得
    app.run(host="0.0.0.0", port=port)
