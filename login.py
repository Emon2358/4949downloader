import sys
import requests
from bs4 import BeautifulSoup

# コマンドライン引数から情報を取得
EMAIL = sys.argv[1]  # ニコニコのメールアドレス
PASSWORD = sys.argv[2]  # ニコニコのパスワード

# セッションを作成
session = requests.Session()

try:
    # ログインページへアクセスして CSRF トークンを取得
    login_page = session.get("https://account.nicovideo.jp/login")
    if login_page.status_code != 200:
        raise Exception(f"ログインページの取得に失敗しました: {login_page.status_code}")
    
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token_input = soup.find("input", {"name": "csrf_token"})
    
    if not csrf_token_input:
        raise Exception("CSRF トークンが見つかりませんでした")
    
    csrf_token = csrf_token_input.get("value")

    # ログインリクエストを送信
    login_data = {
        "mail_tel": EMAIL,
        "password": PASSWORD,
        "csrf_token": csrf_token
    }
    response = session.post("https://account.nicovideo.jp/api/v1/login", data=login_data)

    if response.status_code == 200 and "ログインに成功しました" in response.text:
        print("ログイン成功")
    else:
        raise Exception("ログイン失敗")

    # R-18 設定ページにアクセス
    settings_page = session.get("https://www.nicovideo.jp/my/settings")
    soup = BeautifulSoup(settings_page.text, 'html.parser')

    # R-18 の設定が無効の場合、有効にするリクエストを送信
    r18_checkbox = soup.find("input", {"id": "r18-checkbox"})
    if r18_checkbox and not r18_checkbox.has_attr("checked"):
        r18_data = {
            "r18_enabled": "true",
            "csrf_token": csrf_token
        }
        save_response = session.post("https://www.nicovideo.jp/my/settings", data=r18_data)
        if save_response.status_code == 200:
            print("R-18 コンテンツを有効化しました")
        else:
            raise Exception("R-18 設定の保存に失敗しました")
    else:
        print("R-18 コンテンツは既に有効です")

    # 完了メッセージ
    print("操作が完了しました")

except Exception as e:
    print(f"エラーが発生しました: {e}")
