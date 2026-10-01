# サイトを作り直して GitHub にコミット・プッシュする（download_sheet.ps1 の後に実行）
# プッシュすると GitHub Actions が public/ を FTP でサーバにアップロードする
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

# xlsx は直近 7 個だけ残す
Get-ChildItem -Path $Repo -Filter 'X_post_sheet_*.xlsx' |
    Sort-Object Name -Descending | Select-Object -Skip 7 | Remove-Item -Force

python scripts/build.py
if ($LASTEXITCODE -ne 0) { throw "build.py failed ($LASTEXITCODE)" }

git add public
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Write-Output 'no changes'; exit 0 }

git commit -m ("Update videos " + (Get-Date -Format 'yyyy-MM-dd'))
if ($LASTEXITCODE -ne 0) { throw "git commit failed ($LASTEXITCODE)" }
git push origin main
if ($LASTEXITCODE -ne 0) { throw "git push failed ($LASTEXITCODE)" }
