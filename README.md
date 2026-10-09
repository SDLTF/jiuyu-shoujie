# 九域守界

九域守界的人物设定图集与小说阅读网站。

**访问网站：[sdltf.github.io/jiuyu-shoujie](https://sdltf.github.io/jiuyu-shoujie/)**

目前收录 27 位角色的完整人物展示卡；小说正文尚未发布。

创作大纲单独保存于 `content/outline.md`，包含完整剧情与结局。网站首页不展示大纲内容，大纲页面默认显示剧透提醒，需要主动确认后才会展开。

## 内容与网站

- `content/characters.json`：人物图册清单。
- `assets/originals/`：27 张原始 PNG 图片。
- `content/outline.md`：故事大纲（含剧透）。
- `content/chapters/`：小说正文，使用 Markdown 编写。
- `docs/`：已经生成的静态网站，GitHub Pages 从这里发布。
- `scripts/build.py`：将内容生成网页，并为人物图片生成 WebP 浏览版本。

## 更新网站

首次使用需要 Python 3 和依赖：

```powershell
python -m pip install -r requirements.txt
```

修改内容后：

```powershell
python scripts/build.py
git add .
git commit -m "更新小说与人物设定"
git push
```

也可以在 PowerShell 运行 `./Update-Site.ps1`，完成生成、提交与上传。

正文每章一个文件，例如 `content/chapters/001.md`：

```markdown
# 第一章 春水不回头

在这里写正文。
```

按 `001.md`、`002.md`、`003.md` 命名即可按顺序发布。章节目录与上下章链接会自动生成。文件夹为空时，网站会显示“正文尚未发布”。请勿将大纲当作正文发布。

## 本地预览

```powershell
python -m http.server 8000 --directory docs
```

在浏览器打开 `http://localhost:8000/`。

## 发布设置

GitHub 仓库 → Settings → Pages：

- Source：Deploy from a branch
- Branch：main
- Folder：/docs

推送到 main 后，GitHub Pages 自动更新网站。
