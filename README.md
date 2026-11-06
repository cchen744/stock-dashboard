# Nora 美股看板（独立网站版）

一个纯静态网站，托管在 GitHub Pages 上，不需要登录就能访问，手机和电脑都能看。

## 目录结构

```
index.html                    页面（d3 画图，读取 data/*.json）
data/*.json                   全部数据（字段说明见「美股看板实现备忘录.md」第 4 节）
scripts/update_prices.py      行情更新脚本（yfinance，失败时回退 Alpha Vantage）
.github/workflows/update.yml  每个交易日自动运行行情更新并提交
```

## 上线步骤（约 10 分钟）

1. 在 GitHub 新建仓库，例如 `stock-dashboard`，选 **Public**。免费账号只有公开仓库能用 GitHub Pages；学生包的 GitHub Pro 可以用私有仓库，但网站本身仍然是公开的。
2. 进入仓库页面，选 **Add file → Upload files**，把本文件夹里的**全部内容**拖进去（包括 `.github` 文件夹），然后 Commit。
   - 注意：macOS 默认隐藏以 `.` 开头的文件夹，在 Finder 里按 `Cmd+Shift+.` 可以显示。
   - 网页上传有时会漏掉 `.github` 文件夹。如果漏了，就用 **Add file → Create new file**，文件名填 `.github/workflows/update.yml`，再把内容粘贴进去。
3. 打开 **Settings → Pages**，Source 选 **Deploy from a branch**，Branch 选 `main`，目录选 `/ (root)`，保存。
   大约 1 分钟后，网址会是 `https://cchen744.github.io/stock-dashboard/`。
4. 打开 **Settings → Actions → General → Workflow permissions**，选 **Read and write permissions** 并保存。
5. （可选）打开 **Settings → Secrets and variables → Actions → New repository secret**，名称填 `ALPHAVANTAGE_KEY`，值填你的 Alpha Vantage key，作为行情的备用数据源。
6. 打开 **Actions → 更新行情 → Run workflow** 手动运行一次，确认能正常更新。

## 自动更新

- **行情、指数涨跌、潜力股现价**：GitHub Actions 在每个交易日 UTC 22:17（北京时间次日 06:17）自动更新，免费。
- **新闻风险、机构观点、财报解读、个股判断、分析师观点、双周潜力股**：由 Claude 定时任务写入 `data/` 下对应的 JSON。如果没有接入，这些内容会保持上次的状态。

## 自己修改

- **改文字或数据**：直接在 GitHub 网页上编辑 `data/*.json`，提交后约 1 分钟网站就会更新。
- **增删关注的股票**：编辑 `data/watchlist.json`。个股还需要在 `fundamentals.json`、`analysts.json`、`verdicts.json`、`earnings.json` 里补上对应条目；ETF 不用。
- **改页面**：编辑 `index.html`。页面开头的运行时脚本负责读取数据，后面的部分与 claude.ai 版本的结构相同。
