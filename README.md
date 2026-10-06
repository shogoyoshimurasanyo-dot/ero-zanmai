# ero-zanmai-time

FANZA / MGS / myfans の動画ブロックをプラットフォーム別に並べる静的サイト。FANZA は毎日 100 本入れ替える。

```
[毎朝 7:00 タスクスケジューラ] ..\download_sheet.ps1
  1. GAS からスプレッドシートを xlsx でダウンロード（このフォルダに保存）
  2. scripts/publish.ps1
     - scripts/build.py が public/ を生成
     - public/ に変更があれば commit して GitHub に push
[GitHub Actions] .github/workflows/deploy.yml
  3. public/ を FTP でサーバの FTP_SERVER_DIR にアップロード
```

## ページ構成

| URL | 中身 |
|---|---|
| `/` | `r8tq/`（FANZA）へ転送（`#v-xxx` も引き継ぐ） |
| `/r8tq/` | えろざんまい（FANZA）: シート「API」から 100 本（人気順位上位 30 本＋日替わりランダム。発売済みのみ） |
| `/k3wn/` | MGS: X 投稿用にピックアップした MGS 作品を累積で掲載（下記） |
| `/p6hz/` | myfans: シート「sheet」本文の myfans リンク ＋ シート「myfans」 |

URL のパスは商標を避けるため、サービス名と無関係な値にしている（`scripts/build.py` の `PLATFORMS[].path`）。
上部の固定メニュー（プルダウン）で各ページに移動できる。
シート「MGS」「myfans」は任意。列は `ID` / `タイトル` / `URL` / `画像URL` / `埋め込みHTML` / `説明`。

## MGS タブ（/k3wn/）

- 拾う作品（品番で重複除去）
  - シート「sheet」本文の `https://www.mgstage.com/product/product_detail/<品番>/?aff=…`
    （`fetch_mgs.py` → `publish_gassheet.py` で予約した MGS 投稿）。画像は G 列、無ければ候補の画像
  - シート「sheet」本文の MGS ウィジェット（`mgs_Widget_affiliate`）
  - シート「MGS」（任意）
- タイトル・出演者は、この PC の `xposts/*/mgs_candidates.json` にあればそこから補う（無ければ投稿本文）
- 拾った作品は `public/k3wn/items.json`（品番キー、`first`＝初めて載せた日）に貯める。
  毎回のビルドで追加・更新し、xlsx から消えた作品も残す。ページには全件を `first` の新しい順で出す
- `items.json` が無いときだけ、リポジトリ直下の過去の xlsx（最大 7 個）からも拾う
  （作り直したいときは `items.json` を消してビルド。ただし 7 個より古い xlsx の作品は戻らない）

## SNS 用の直リンク

各動画ブロックは `id="v-<ID>"` を持つので、次の URL でそのブロックの位置に移動する。

```
https://<サイト>/r8tq/#v-<content_id>       例: /r8tq/#v-1namh00064
https://<サイト>/k3wn/#v-<品番(小文字)>       例: /k3wn/#v-abf-331
https://<サイト>/p6hz/#v-<リンクのコード(小文字)>
```

- 各ブロックの「リンクをコピー」ボタンでこの URL をコピーできる
- 一度掲載したブロックは `<platform>/catalog.json` に貯める。日替わりでページから消えたブロックの
  リンクを開いた場合は、catalog.json から「シェアされた動画」としてページ先頭に差し込んで移動する
  （最後に掲載した日が新しい順に最大 3000 件）

## ファイル

- `scripts/build.py` … xlsx を読んでページを生成（プラットフォーム追加は `PLATFORMS` と `LOADERS`）
- `scripts/template.html` … 各プラットフォームページの雛形
- `static/` … 共通 CSS / JS（`public/assets/` にコピーされる）
- `public/` … 生成物（手で編集しない）

## 初回設定

1. `pip install -r requirements.txt`
2. GitHub の Settings → Secrets and variables → Actions に
   `FTP_SERVER` / `FTP_USERNAME` / `FTP_PASSWORD` / `FTP_SERVER_DIR` を登録

## 手動で動かす

```powershell
python scripts/build.py          # public/ を作るだけ
.\scripts\publish.ps1            # 作って commit・push まで
```

xlsx（DMM API ID や X 投稿データを含む）と download_log.txt は `.gitignore` で除外している。
