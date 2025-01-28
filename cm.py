import json
import re
import requests

from bs4 import BeautifulSoup

movie_id = "sm9"  # 動画 ID

url = f"https://www.nicovideo.jp/watch/{movie_id}"
source = requests.get(f"https://nicovideo.jp/watch/{movie_id}")
soup = BeautifulSoup(source.text, "html.parser")
soup = str(soup)

threadIdRegex = r'threadIds":\[\{"id":(.*?),"'
threadKeyRegex = r'"threadKey":"(eyJ0eXAiOiJKV1Qi.*?)"'

threadId = re.findall(threadIdRegex, soup)[0]
threadKey = re.findall(threadKeyRegex, soup)[0]

headers = {"x-frontend-id": "6"}
params = {
    "params": {
        "targets":[
            {
                "id": threadId,
                "fork": "owner"  # 投稿者コメント
            },
            {
                "id": threadId,
                "fork": "main"  # 通常コメント
            },
            {
                "id": threadId,
                "fork": "easy"  # かんたんコメント
            }
        ],
        "language": "ja-jp"
    },
    "threadKey": threadKey,
    "additionals": {},
}
endpoint = "https://public.nvcomment.nicovideo.jp/v1/threads"
res = requests.post(endpoint, json.dumps(params), headers=headers).json()

comment_data = res["data"]["threads"]
# comment_data[0] : 投稿者コメント
# comment_data[1] : 通常コメント
# comment_data[2] : かんたんコメント

comment_type = ["投稿者コメント", "通常コメント", "かんたんコメント"]
for n in range(3):
    print(comment_type[n])
    for d in sorted(comment_data[n]["comments"], key=lambda x:x["vposMs"]):
        # d["vposMs"] : コメントの動画内時刻[ms]
        minutes = d["vposMs"] // (1000 * 60)
        seconds = d["vposMs"] // 1000 % 60

        comment = d['body']

        print(f"{minutes:0>2}:{seconds:0>2}\t{comment}")
    print()
