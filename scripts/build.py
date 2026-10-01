#!/usr/bin/env python3
"""
最新の X_post_sheet_YYYYMMDD.xlsx（シート「API」）から 100 作品を選び、
public/index.html と public/videos.json を作る。

選び方:
  1. 発売日が今日以前の作品だけを対象にする（未発売はサンプル動画がないため）
  2. 人気順位がある作品を、順位の高い順に最大 KEEP_RANKED 件
  3. 残りの枠を、ほかの作品から日付をシードにランダムで埋める（毎日入れ替わる）

使い方:
  python scripts/build.py              リポジトリ直下の最新 xlsx を使う
  python scripts/build.py path.xlsx    xlsx を指定する
"""
import datetime as dt
import html
import json
import random
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
JST = dt.timezone(dt.timedelta(hours=9))
TODAY = dt.datetime.now(JST).date()

SHEET = "API"
COUNT = 100
KEEP_RANKED = 30
SITE_TITLE = "エロ三昧タイム"
# サンプル動画プレイヤー（litevideo）用のアフィリエイト ID
PLAYER_AFFI_ID = "NUBh0jCpE9kc-001"
PLAYER_URL = ("https://www.dmm.co.jp/litevideo/-/part/=/affi_id={affi}"
              "/cid={cid}/size=1280_720/")


def find_xlsx(argv):
    if len(argv) > 1:
        return Path(argv[1])
    files = sorted(ROOT.glob("X_post_sheet_*.xlsx"))
    if not files:
        sys.exit("X_post_sheet_*.xlsx が見つかりません。")
    return files[-1]


def as_date(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return None


def read_items(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = wb[SHEET].iter_rows(values_only=True)
    header = [str(h).strip() if h is not None else "" for h in next(rows)]
    col = {name: i for i, name in enumerate(header) if name}

    def get(row, name):
        i = col.get(name)
        v = row[i] if i is not None and i < len(row) else None
        return v.strip() if isinstance(v, str) else v

    items, seen = [], set()
    for row in rows:
        cid = get(row, "content_id")
        if not cid or cid in seen:
            continue
        released = as_date(get(row, "発売日"))
        if released is None or released > TODAY:
            continue
        seen.add(cid)
        rank = get(row, "人気順位")
        items.append({
            "cid": cid,
            "title": get(row, "タイトル") or "",
            "url": get(row, "アフィリエイトURL") or get(row, "通常URL") or "",
            "image": get(row, "画像URL(大)") or get(row, "画像URL(リスト)") or "",
            "actress": get(row, "女優") or "",
            "maker": get(row, "メーカー") or "",
            "price": get(row, "価格") or "",
            "released": released.isoformat(),
            "rank": int(rank) if isinstance(rank, (int, float)) else None,
        })
    return items


def choose(items):
    ranked = sorted((i for i in items if i["rank"]), key=lambda i: i["rank"])
    picked = ranked[:KEEP_RANKED]
    rest = [i for i in items if i not in picked]
    rng = random.Random(TODAY.isoformat())
    picked += rng.sample(rest, min(COUNT - len(picked), len(rest)))
    return picked


def render_card(n, item):
    e = html.escape
    player = PLAYER_URL.format(affi=PLAYER_AFFI_ID, cid=item["cid"])
    meta = " / ".join(x for x in (item["actress"], item["released"]) if x)
    badge = f'<span class="rank">人気{item["rank"]}位</span>' if item["rank"] else ""
    return f"""      <li class="card">
        <button class="thumb" type="button" data-player="{e(player)}" aria-label="{e(item['title'])} のサンプル動画を再生">
          <img src="{e(item['image'])}" alt="" loading="lazy" decoding="async">
          <span class="play" aria-hidden="true"></span>{badge}
        </button>
        <div class="body">
          <p class="title">{n}. {e(item['title'])}</p>
          <p class="meta">{e(meta)}</p>
          <a class="cta" href="{e(item['url'])}" target="_blank" rel="sponsored nofollow noopener">FANZAで詳細を見る</a>
        </div>
      </li>"""


def render_page(picked):
    cards = "\n".join(render_card(n, i) for n, i in enumerate(picked, 1))
    template = (ROOT / "scripts" / "template.html").read_text(encoding="utf-8")
    return (template
            .replace("{{SITE_TITLE}}", html.escape(SITE_TITLE))
            .replace("{{DATE}}", f"{TODAY.year}年{TODAY.month}月{TODAY.day}日")
            .replace("{{COUNT}}", str(len(picked)))
            .replace("{{CARDS}}", cards))


def main():
    path = find_xlsx(sys.argv)
    items = read_items(path)
    picked = choose(items)
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(render_page(picked), encoding="utf-8")
    (OUT / "videos.json").write_text(
        json.dumps({"date": TODAY.isoformat(), "items": picked}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    # ログ（cp932）で化けないよう ASCII で出す
    print(f"{path.name}: picked {len(picked)} of {len(items)} released items")


if __name__ == "__main__":
    main()
