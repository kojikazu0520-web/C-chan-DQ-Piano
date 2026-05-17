# Project_codex

このワークスペースは用途ごとにフォルダを分けています。

## youtube-hp

`youtube-hp/` は、YouTubeチャンネル「しーちゃんピアノ」のホームページ一式です。

- 静的HTML/CSS/JS
- 作品別ページ
- カテゴリ別ページ
- YouTubeプレイリストデータ
- サイトマップ

ローカル確認:

```bash
cd youtube-hp
python3 -m http.server 8123
```

ブラウザで `http://127.0.0.1:8123/` を開きます。

## sedori_works

`sedori_works/` は、せどり系のCSV分析・価格差チェック・管理シート関連の作業フォルダです。

## discord-bot

`discord-bot/` は、Discord通知や分析結果連携の作業フォルダです。
