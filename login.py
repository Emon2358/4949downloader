# login.py
import requests

LOGIN_URL = "https://account.nicovideo.jp/api/v1/login"
SETTINGS_URL = "https://www.nicovideo.jp/api/v1/user.settings.update"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def login_and_set_preferences(email, password):
    session = requests.Session()

    # ログインリクエスト
    payload = {
        "mail_tel": email,
        "password": password
    }
    response = session.post(LOGIN_URL, headers=HEADERS, data=payload)

    if response.status_code == 200 and "nicosid" in session.cookies:
        print("Login successful")

        # 卑猥な動画（R-18）を表示する設定を有効化
        settings_payload = {
            "r18_enabled": "true"  # 設定変更: R-18動画を有効化
        }
        settings_response = session.post(SETTINGS_URL, headers=HEADERS, data=settings_payload, cookies=session.cookies)

        if settings_response.status_code == 200:
            print("Account settings updated: R-18 videos enabled")

        # クッキーを保存
        with open("cookies.txt", "w") as f:
            for key, value in session.cookies.items():
                f.write(f"{key}\t{value}\n")
        print("Cookies saved to cookies.txt")
    else:
        print("Login failed")
        exit(1)


if __name__ == "__main__":
    import sys
    email = sys.argv[1]
    password = sys.argv[2]
    login_and_set_preferences(email, password)
