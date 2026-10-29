# Chenyuan Feng / 冯晨远 — Academic website

中英双语学术主页，使用与参考网站相同的 **Jekyll + Just the Docs** 架构、布局与 SCSS 样式。包含首页、科研项目、学术成果、招生招聘、联系方式和学术简历。

## 本地运行

使用 Ruby 3.3 与 Bundler：

```bash
bundle install
bash scripts/dev.sh
```

本地地址：`http://127.0.0.1:4175/`。中文首页：`http://127.0.0.1:4175/zh/`。

在本次工作区中，`scripts/dev.sh` 会自动使用已准备好的本地 Ruby 环境。其他电脑按上面的标准 Ruby / Bundler 流程运行即可。

## 修改内容

- `index.md`、`zh/index.md`：中英文首页。
- `websites/`、`zh/websites/`：科研项目、学术成果、招生招聘、联系方式、简历。
- `_data/publications_en.json`、`_data/publications_zh.json`：95 项成果，保留 CV 的五类分组及中英文期刊指标。
- `_data/cv_en.json`、`_data/cv_zh.json`：教育、工作、项目、荣誉、报告、学术服务与专利。
- `assets/resume/`：中英文 PDF 简历。
- `assets/bibliography/references.bib`：93 条 BibTeX 书目。
- `_sass/custom/custom.scss`：原站完整样式系统。
- `assets/css/feng.css`：论文指标与网页版 CV 的少量样式补充。

从更新后的双语 LaTeX CV 重新导入内容：

```bash
python3 scripts/import_cv.py /path/to/feng_chenyuan_cv_bilingual
```

导入后，首页的简短介绍及 PDF 文件可按需同步更新。

## 构建与 GitHub Pages

```bash
bundle exec jekyll build
```

网站地址：**https://chenyuanuni.github.io/**。

保留了原站 `.github/workflows/` 中的构建与部署流程。推送 `main` 分支会构建并发布 GitHub Pages；仓库 Settings → Pages 的 Source 应设置为 GitHub Actions。域名与路径在 `_config.yml` 中配置；使用自定义域名时再添加 `CNAME`。
