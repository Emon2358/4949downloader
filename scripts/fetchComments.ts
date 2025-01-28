import { ThreadIdFetchError, ThreadKeyFetchError } from "./error.ts";

interface ThreadRequestBody {
    params: {
        targets: {
            id: string;
            fork: "owner" | "main" | "easy";
        }[];
        language: "ja-jp";
    };
    threadKey: string;
    additionals: Record<string | number | symbol, never>;
}

interface ThreadResponse {
    meta: {
        status: number;
    };
    data: {
        globalComments: {
            id: string;
            count: number;
        }[];
        threads: {
            id: number;
            fork: "owner" | "main" | "easy";
            commentCount: number;
            comments: {
                id: string;
                no: number;
                vposMs: number;
                body: string;
                commands: string[];
                userId: string;
                isPremium: boolean;
                score: number;
                postedAt: string;
                nicoruCount: number;
                nicoruId: string | null;
                source: "trunk" | "leaf" | "nicoru";
                isMyPost: boolean;
            }[];
        }[];
    };
}

// 入力されたsm番号からニコニコ動画のコメントを取得する
export async function fetchComments(videoId: string): Promise<void> {
    const url = `https://www.nicovideo.jp/watch/${videoId}`;
    const endpoint = "https://public.nvcomment.nicovideo.jp/v1/threads";
    const threadIdRegex = /threadIds&quot;:\[\{&quot;id&quot;:(.*?),&quot;/;
    const threadKeyRegex = /{&quot;threadKey&quot;:&quot;(eyJ0eXAiOiJKV1Qi.*?)&quot/;

    // 動画ページを取得
    const videoPage = await (await fetch(url)).text();
    const threadId = videoPage.match(threadIdRegex)?.[1];
    const threadKey = videoPage.match(threadKeyRegex)?.[1];

    // スレッドIDまたはスレッドキーが取得できない場合のエラー
    if (!threadId) {
        throw new ThreadIdFetchError("スレッドIDの取得に失敗しました。");
    }
    if (!threadKey) {
        throw new ThreadKeyFetchError("スレッドキーの取得に失敗しました。");
    }

    // リクエストペイロード
    const payload: ThreadRequestBody = {
        params: {
            targets: [
                { id: threadId, fork: "owner" },
                { id: threadId, fork: "main" },
                { id: threadId, fork: "easy" },
            ],
            language: "ja-jp",
        },
        threadKey: threadKey,
        additionals: {},
    };

    // コメント取得APIを呼び出し
    const response = await fetch(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
        headers: { "x-frontend-id": "6" },
    });
    const data = (await response.json()) as ThreadResponse;

    // コメントを表示
    data.data.threads.forEach((thread) => {
        console.log(`コメントタイプ: ${thread.fork}`);
        thread.comments.forEach((comment) => {
            const time = `${Math.floor(comment.vposMs / 60000)}:${Math.floor((comment.vposMs % 60000) / 1000)}`;
            console.log(`[${time}] ${comment.body}`);
        });
    });
}

// GitHub Actions から動画IDを渡す
const videoId = Deno.args[0];
if (videoId) {
    fetchComments(videoId).catch((error) => {
        console.error("エラーが発生しました:", error);
    });
} else {
    console.error("動画IDが指定されていません。");
}
