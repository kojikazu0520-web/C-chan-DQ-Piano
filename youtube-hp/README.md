# しーちゃんピアノ YouTube HP

YouTubeチャンネル「しーちゃんピアノ」の静的ホームページです。

## 主なファイル

- `index.html`: 日本語トップページ
- `en/index.html`: 英語トップページ
- `styles.css`: 共通スタイル
- `site-content.js`: 表示文言
- `playlist-data.js`: YouTubeプレイリスト/動画データ
- `song-reference-data.js`: 作品別の曲データ
- `build-seo-pages.py`: 作品別・カテゴリ別ページ生成
- `sync-podcasts.py`: YouTubeポッドキャスト/プレイリスト取得
- `covers/`: プレイリストサムネイル
- `dq1/`〜`dq11/`: 作品別ページ
- `category/`: カテゴリ別ページ

## ローカル確認

```bash
python3 -m http.server 8123
```

`http://127.0.0.1:8123/` を開いて確認します。
