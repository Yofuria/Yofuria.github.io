# Xiaobo Wang's personal website

[Homepage](https://yofuria.github.io/) · [All publications](https://yofuria.github.io/pages/all-publications.html) · [All news](https://yofuria.github.io/pages/all-news.html) · [SAVE](https://yofuria.github.io/projects/save/)

A static academic website with a single-column layout, built with HTML, CSS, JavaScript, and JSON. GitHub Pages publishes the root of the `main` branch. [中文维护说明](docs/README-zh.md).

## Updating content

| File | Purpose |
| --- | --- |
| `index.html` | Biography, research interests and directions, projects, education, experience, academic service, and contact details |
| `data/publications.json` | Publication titles, authors, venues, years, first-author flags, and resource links |
| `data/news.json` | News in newest-first order; the homepage shows the first three items and the news archive shows every item |
| `pages/all-publications.html` | Full publication list and filters; entries are generated from the publication JSON |
| `pages/all-news.html` | Full news archive; entries are generated from the news JSON |
| `projects/save/index.html` | SAVE project description, figure, abstract, method, resource links, and BibTeX |
| `homepage.css` | Shared layout and styling for all four pages |
| `script.js` | Shared JSON loading, publication filters, links, and current year |
| `assets/`, `images/` | Profile image, institution logos, publication assets, and favicons |

Keep publication and news content in the JSON files so that the homepage and archives stay in sync. Keep news in newest-first order. Update the shared stylesheet or script version in all four HTML files when those assets change; this refreshes cached copies on every page.

## Preview locally

No build step or Jekyll installation is needed. From the repository directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open [the local preview](http://127.0.0.1:8000/). Check the homepage, both archives, and the SAVE page at desktop and mobile widths. Publication filters and return links should work, and images should load.

## Publish

Commit the changed files and push to `main`. GitHub Pages deploys automatically. Verify that the latest **pages build and deployment** run succeeds and that the corresponding pages display the update.

## Citation crawler

`.github/workflows/google_scholar_crawler.yaml` runs daily at 09:37 UTC (17:37 China time) and can also be run manually. It writes citation JSON to the `google-scholar-stats` branch. The crawler uses the `GOOGLE_SCHOLAR_ID` secret and the optional `SCRAPERAPI_KEY` secret.

## Template acknowledgments

The site retains a credit to [AcaNova-X](https://github.com/yihangtao/AcaNova-X). Original AcadHomepage acknowledgments:

- AcadHomepage incorporates Font Awesome, which is distributed under the terms of the SIL OFL 1.1 and MIT License.
- AcadHomepage is influenced by the github repo [mmistakes/minimal-mistakes](https://github.com/mmistakes/minimal-mistakes), which is distributed under the MIT License.
- AcadHomepage is influenced by the github repo [academicpages/academicpages.github.io](https://github.com/academicpages/academicpages.github.io), which is distributed under the MIT License.
