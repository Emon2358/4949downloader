from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

# コマンドライン引数からメールアドレスとパスワードを取得
EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]

# Chromeオプション（ヘッドレスモードで実行）
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ブラウザを初期化
driver = webdriver.Chrome(options=options)
driver.maximize_window()

try:
    # ニコニコ動画のログインページにアクセス
    driver.get("https://account.nicovideo.jp/login")

    # メールアドレスを入力
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input__mailtel"))
    )
    email_input.send_keys(EMAIL)

    # パスワードを入力
    password_input = driver.find_element(By.ID, "input__password")
    password_input.send_keys(PASSWORD)

    # ログインボタンをクリック
    login_button = driver.find_element(By.ID, "login__submit")
    login_button.click()

    # ログイン成功を待機
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "MainContainer"))
    )
    print("ログイン成功")

    # R-18設定ページに移動
    driver.get("https://www.nicovideo.jp/my/settings")

    # R-18コンテンツの有効化
    r18_checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "r18-checkbox"))  # 正確なIDを確認してください
    )
    if not r18_checkbox.is_selected():
        r18_checkbox.click()
        print("R-18コンテンツを有効化しました")
    else:
        print("R-18コンテンツは既に有効です")

    # 設定を保存
    save_button = driver.find_element(By.ID, "save-settings")
    save_button.click()
    print("設定を保存しました")

    # クッキーを保存
    with open("cookies.txt", "w") as f:
        for cookie in driver.get_cookies():
            f.write(f"{cookie['name']}={cookie['value']}; ")

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    # ブラウザを閉じる
    time.sleep(5)
    driver.quit()
