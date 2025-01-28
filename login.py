from playwright.sync_api import sync_playwright
import sys

# ユーザー情報
EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]

# Playwrightを使用してブラウザを操作
with sync_playwright() as p:
    # Chromiumブラウザを起動
    browser = p.chromium.launch(headless=True)  # headless=True でブラウザを非表示
    page = browser.new_page()

    # ニコニコのログインページにアクセス
    page.goto("https://account.nicovideo.jp/login")

    # メールアドレスとパスワードを入力
    page.fill("input[name='mail_tel']", EMAIL)
    page.fill("input[name='password']", PASSWORD)

    # ログインボタンをクリック
    page.click("button[type='submit']")

    # ログイン後のページが読み込まれるまで待機
    page.wait_for_url("https://www.nicovideo.jp/my")
    print("ログイン成功")

    # R-18設定ページにアクセス
    page.goto("https://www.nicovideo.jp/my/settings")

    # R-18コンテンツのチェックボックスを確認
    r18_checkbox = page.query_selector("input#r18-checkbox")

    if r18_checkbox:
        # R-18チェックボックスがチェックされていない場合は有効にする
        if not r18_checkbox.is_checked():
            # R-18を有効化するためにチェックを入れる
            page.check("input#r18-checkbox")
            page.click("button[type='submit']")  # 設定を保存するためにボタンをクリック
            print("R-18 コンテンツを有効化しました")
        else:
            print("R-18 コンテンツは既に有効です")
    else:
        print("R-18設定のチェックボックスが見つかりませんでした")

    # クッキーを取得して保存
    cookies = page.context.cookies()
    with open("cookies.txt", "w") as cookie_file:
        for cookie in cookies:
            cookie_file.write(f"{cookie['name']}={cookie['value']}\n")

    # ブラウザを閉じる
    browser.close()
