import re
import requests
import sys
import os

class ThreadIdFetchError(Exception):
    pass

class ThreadKeyFetchError(Exception):
    pass

def fetch_comments(video_id: str, output_file: str):
    url = f"https://www.nicovideo.jp/watch/{video_id}"
    endpoint = "https://public.nvcomment.nicovideo.jp/v1/threads"
    thread_id_regex = re.compile(r'threadIds&quot;:\[\{&quot;id&quot;:(.*?),&quot;')
    thread_key_regex = re.compile(r'{&quot;threadKey&quot;:&quot;(eyJ0eXAiOiJKV1Qi.*?)&quot')

    # 動画ページのHTMLを取得
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch video page. Status code: {response.status_code}")
    video_page = response.text

    # threadId と threadKey を抽出
    thread_id_match = thread_id_regex.search(video_page)
    thread_key_match = thread_key_regex.search(video_page)
    if not thread_id_match:
        raise ThreadIdFetchError("Thread ID not found.")
    if not thread_key_match:
        raise ThreadKeyFetchError("Thread Key not found.")

    thread_id = thread_id_match.group(1)
    thread_key = thread_key_match.group(1)

    # コメント取得リクエストのペイロード
    payload = {
        "params": {
            "targets": [
                {"id": thread_id, "fork": "owner"},
                {"id": thread_id, "fork": "main"},
                {"id": thread_id, "fork": "easy"}
            ],
            "language": "ja-jp"
        },
        "threadKey": thread_key,
        "additionals": {}
    }

    # コメント取得リクエストを送信
    headers = {"x-frontend-id": "6"}
    thread_response = requests.post(endpoint, json=payload, headers=headers)
    if thread_response.status_code != 200:
        raise Exception(f"Failed to fetch comments. Status code: {thread_response.status_code}")

    comments = thread_response.json()

    # 出力先ディレクトリを作成（存在しない場合）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # コメントをファイルに保存
    with open(output_file, "w", encoding="utf-8") as f:
        for thread in comments.get("data", {}).get("threads", []):
            for comment in thread.get("comments", []):
                try:
                    time = float(comment.get("vposMs", 0)) / 1000  # 秒単位に変換
                    body = comment.get("body", "").replace("\n", " ")  # 改行を除去
                    if body:  # コメントが空でない場合のみ保存
                        f.write(f"{time} {body}\n")
                except (ValueError, TypeError):
                    # vposMs が無効な値の場合はスキップ
                    continue

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_comments.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    output_file = f"downloads/{video_id}_comments.txt"
    try:
        fetch_comments(video_id, output_file)
        print(f"Comments saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
