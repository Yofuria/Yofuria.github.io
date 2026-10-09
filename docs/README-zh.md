# Xiaobo Wang 个人主页维护说明

[主页](https://yofuria.github.io/) · [全部论文](https://yofuria.github.io/pages/all-publications.html) · [全部动态](https://yofuria.github.io/pages/all-news.html) · [SAVE 项目页](https://yofuria.github.io/projects/save/)

网站使用 HTML、CSS、JavaScript 和 JSON，四个页面共用简洁单栏样式。GitHub Pages 从 `main` 分支的根目录发布。[English documentation](../README.md)。

## 修改内容

| 文件 | 用途 |
| --- | --- |
| `index.html` | 简介、研究兴趣和方向、项目、教育、经历、学术服务及联系方式 |
| `data/publications.json` | 论文标题、作者、会议或期刊、年份、第一作者标记及资源链接 |
| `data/news.json` | 按时间从新到旧排列的动态；首页显示前三条，完整动态页显示全部 |
| `pages/all-publications.html` | 完整论文列表和筛选入口，论文内容从 JSON 加载 |
| `pages/all-news.html` | 完整动态页，内容从 JSON 加载 |
| `projects/save/index.html` | SAVE 项目介绍、示意图、摘要、方法说明、资源链接和 BibTeX |
| `homepage.css` | 四个页面共用的布局和样式 |
| `script.js` | 共用的数据加载、论文筛选、链接处理和年份更新 |
| `assets/`、`images/` | 头像、机构 logo、论文资源和网站图标 |

论文和动态的内容统一在 JSON 文件中维护，首页及完整列表页会同步读取。动态按时间从新到旧排列。修改共用样式或脚本时，同步更新四个 HTML 文件引用中的版本号，让各页面刷新缓存。

## 本地预览

无需安装 Jekyll 或运行构建。在仓库目录执行：

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

打开[本地预览](http://127.0.0.1:8000/)，检查主页、两个列表页和 SAVE 项目页的桌面及手机布局，同时确认论文筛选、返回链接和图片加载正常。

## 发布

提交修改并推送到 `main`，GitHub Pages 会自动部署。确认最新的 **pages build and deployment** 运行成功，再打开对应的线上页面核对更新。

## 学术引用爬虫

`.github/workflows/google_scholar_crawler.yaml` 每天 09:37 UTC（北京时间 17:37）运行，也支持手动运行。结果以 JSON 写入 `google-scholar-stats` 分支。爬虫使用 `GOOGLE_SCHOLAR_ID` secret，并支持可选的 `SCRAPERAPI_KEY` secret。

## 模板致谢

网站保留了 [AcaNova-X](https://github.com/yihangtao/AcaNova-X) 的署名。原 AcadHomepage 模板的致谢如下：

- AcadHomepage incorporates Font Awesome, which is distributed under the terms of the SIL OFL 1.1 and MIT License.
- AcadHomepage is influenced by the github repo [mmistakes/minimal-mistakes](https://github.com/mmistakes/minimal-mistakes), which is distributed under the MIT License.
- AcadHomepage is influenced by the github repo [academicpages/academicpages.github.io](https://github.com/academicpages/academicpages.github.io), which is distributed under the MIT License.
