"""每个美股交易日运行：更新 data/prices.json、data/market.json 的指数行、data/picks.json 的价格。

数据源：yfinance（免费、无需 key）；若失败且设置了环境变量 ALPHAVANTAGE_KEY，则回退到 Alpha Vantage。
写入前做校验，任何一步失败都不会覆盖旧数据。
"""
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent.parent / "data"
WINDOW = 21  # 保留的交易日数


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def save(name, obj):
    (DATA / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def closes_yf(tickers, period="3mo"):
    import yfinance as yf
    df = yf.download(tickers, period=period, interval="1d", auto_adjust=False, progress=False, group_by="ticker", threads=True)
    out = {}
    for t in tickers:
        try:
            s = df[t]["Close"].dropna()
        except Exception:
            continue
        if len(s):
            out[t] = {d.strftime("%Y-%m-%d"): round(float(v), 4) for d, v in s.items()}
    return out


def closes_av(tickers):
    key = os.environ.get("ALPHAVANTAGE_KEY")
    if not key:
        return {}
    out = {}
    for t in tickers:
        r = requests.get("https://www.alphavantage.co/query", params={"function": "TIME_SERIES_DAILY", "symbol": t, "outputsize": "compact", "apikey": key}, timeout=30)
        ts = r.json().get("Time Series (Daily)", {})
        if ts:
            out[t] = {d: float(v["4. close"]) for d, v in ts.items()}
        time.sleep(1.5)
    return out


def get_closes(tickers):
    data = {}
    try:
        data = closes_yf(tickers)
    except Exception as e:
        print("yfinance failed:", e, file=sys.stderr)
    missing = [t for t in tickers if t not in data]
    if missing:
        print("fallback to Alpha Vantage for", missing, file=sys.stderr)
        data.update(closes_av(missing))
    return data


def update_prices():
    tickers = [w["ticker"] for w in load("watchlist")]
    data = get_closes(tickers)
    if any(t not in data for t in tickers):
        raise SystemExit(f"missing tickers: {[t for t in tickers if t not in data]}")
    common = sorted(set.intersection(*(set(v) for v in data.values())))[-WINDOW:]
    if len(common) < WINDOW:
        raise SystemExit("not enough aligned trading days")
    old = load("prices")
    old_last = max(r["date"] for r in old) if old else ""
    if common[-1] < old_last:
        raise SystemExit("new data older than existing data; abort")
    for t in tickers:  # 单日 ±25% 以上的异常值直接中止，交给人工核对
        a, b = data[t][common[-2]], data[t][common[-1]]
        if abs(b / a - 1) > 0.25:
            raise SystemExit(f"{t} moved {b / a - 1:.1%} in one day; please verify manually")
    rows = [{"ticker": t, "date": d, "close": round(data[t][d], 2)} for t in tickers for d in common]
    save("prices", rows)
    print("prices updated to", common[-1])
    return common[-1]


INDEX = {"纳斯达克综合": "^IXIC", "标普 500": "^GSPC", "道琼斯": "^DJI", "10 年期美债": "^TNX", "VIX": "^VIX"}


def update_market():
    try:
        data = closes_yf(list(INDEX.values()), period="1mo")
    except Exception as e:
        print("market update skipped:", e, file=sys.stderr)
        return
    market = load("market")
    for row in market:
        key = next((k for k in INDEX if row["item"].startswith(k)), None)
        if not key or INDEX[key] not in data:
            continue  # 加息概率等由 Claude 定时任务维护
        s = data[INDEX[key]]
        ds = sorted(s)
        last, prev = s[ds[-1]], s[ds[-2]]
        if key == "VIX":
            row["item"] = "VIX"
            row["note"] = f"{ds[-1]} 收盘"
        if row.get("unit") == "点":
            row["value"] = round(last)
            row["chg_pct"] = round((last / prev - 1) * 100, 2)
        else:
            row["value"] = round(last, 2)
    save("market", market)
    print("market updated")


def update_picks(last_day):
    picks = load("picks")
    if not picks:
        return
    data = get_closes([p["ticker"] for p in picks])
    for p in picks:
        s = data.get(p["ticker"])
        if s:
            d = max(s)
            p["price"], p["price_date"] = round(s[d], 2), d
    save("picks", picks)
    print("picks prices updated")


if __name__ == "__main__":
    last = update_prices()
    update_market()
    update_picks(last)
