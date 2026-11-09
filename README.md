# 美股看板

不是很想公开但是不公开就没办法看到网站lol
自己做着玩的一个美股科技看板，里面是自己目前的portfolio
依然是谢谢Claude老师～

## 目录结构

```
index.html                    页面（d3 画图，读取 data/*.json）
data/*.json                   全部数据（字段说明见「美股看板实现备忘录.md」第 4 节）
scripts/update_prices.py      行情更新脚本（yfinance，失败时回退 Alpha Vantage）
.github/workflows/update.yml  每个交易日自动运行行情更新并提交
```

## 自动更新

- **行情、指数涨跌、潜力股现价**：GitHub Actions 在每个交易日 UTC 17:00（北京时间次日 5:00）自动更新，免费。
- **新闻风险、机构观点、财报解读、个股判断、分析师观点、双周潜力股**：由定时任务写入 `data/` 下对应的 JSON。如果没有接入，这些内容会保持上次的状态。

## 修改指南

- **改文字或数据**：直接在 GitHub 网页上编辑 `data/*.json`，提交后约 1 分钟网站就会更新。
- **增删关注的股票**：编辑 `data/watchlist.json`。个股还需要在 `fundamentals.json`、`analysts.json`、`verdicts.json`、`earnings.json` 里补上对应条目；ETF 不用。
- **改页面**：编辑 `index.html`。页面开头的运行时脚本负责读取数据。
