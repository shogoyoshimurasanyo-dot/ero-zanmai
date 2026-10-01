# ero-zanmai-time

FANZA の作品を毎日 100 本入れ替えて表示する静的サイト。

```
[毎朝 7:00 タスクスケジューラ] ..\download_sheet.ps1
  1. GAS からスプレッドシートを xlsx でダウンロード（このフォルダに保存）
  2. scripts/publish.ps1
     - scripts/build.py がシート「API」から 100 本を選び public/ を生成
     - public/ に変更があれば commit して GitHub に push
[GitHub Actions] .github/workflows/deploy.yml
  3. public/ を FTP でサーバの FTP_SERVER_DIR にアップロード
```

## 100 本の選び方（scripts/build.py）

- 発売日が今日以前の作品だけ（未発売はサンプル動画がない）
- 人気順位がある作品を上位から最大 30 本（`KEEP_RANKED`）
- 残りはほかの作品から日付をシードにランダム（毎日入れ替わる）
- サムネイルをクリックしたときにサンプル動画プレイヤーを読み込む

## 初回設定

1. `pip install -r requirements.txt`
2. GitHub の Settings → Secrets and variables → Actions に次を登録
   `FTP_SERVER` / `FTP_USERNAME` / `FTP_PASSWORD` / `FTP_SERVER_DIR`（例 `ero/`、末尾 `/` 必須）
   未設定の間はデプロイをスキップする

## 手動で動かす

```powershell
python scripts/build.py          # public/ を作るだけ
.\scripts\publish.ps1            # 作って commit・push まで
```

xlsx（DMM API ID や X 投稿データを含む）と download_log.txt は `.gitignore` で除外している。
