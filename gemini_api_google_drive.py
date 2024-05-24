# ライブラリをインポート
import google.generativeai as genai
import os
import pandas as pd
from pprint import pprint
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload

# APIキーを取得 (GCP上で作成したAPIキー)
gemini_api_key = os.getenv("YOUR_API_KEY")

# APIキーを設定
genai.configure(api_key=gemini_api_key)

# クレデンシャルを設定 (GCPのサービスアカウントのキー)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your_project_credentials.json"

# 利用可能なモデルを確認
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)

# モデルを設定
generation_config = {
  "temperature": 0,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

# セーフティを設定
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

# モデルを作成
model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# 質問を設定
prompt_parts = [
  "Mojoとはどんなプログラミング言語ですか?",
]

# 回答を取得
response = model.generate_content(prompt_parts).text
print(response)

# 回答を格納する空のリスト
answers_list = []

# 回答をリストに追加
answers_list.append(response)

# リストを確認
pprint(answers_list)

# データフレームを作成
df = pd.DataFrame(
    {
        "question": prompt_parts,
        "answer": answers_list
    }
)

# データフレームを確認
pprint(df)

# データフレームをCSV(BOM付き)にエクスポート
df.to_csv("question_and_answer.csv", index=False, encoding="utf_8_sig")

"""
CSVをGoogle ドライブにアップロード
"""

# スコープ
SCOPES = ["https://www.googleapis.com/auth/drive"]

# サービスアカウントファイル
CREDENTIALS_FILE = "your_seccount_file.json"

# クレデンシャル
credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)

# Google Drive API サービスの構築
drive = build("drive", "v3", credentials=credentials)

# ファイル名
file_name = "question_and_answer.csv"

# フォルダID (GoogleドライブのフォルダのURLのhttps://drive.google.com/drive/folders/〜の部分)
folder_id = "your_folder_id"

# ファイルのメタデータ
metadata = {
    "name": file_name,
    "parents": [folder_id]
}

# メインボディを指定
media_body = MediaFileUpload(file_path, resumable=True)

# アップロードを実行
drive.files().create(body=metadata, media_body=media_body).execute()