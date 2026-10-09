# 九域守界

九域守界的人物设定图集与小说阅读网站。

**访问网站：[sdltf.github.io/jiuyu-shoujie](https://sdltf.github.io/jiuyu-shoujie/)**

目前收录 28 位角色，新增[环（张瑞康）](https://sdltf.github.io/jiuyu-shoujie/gallery/28.html)。人物列表显示头像，点击后进入独立人物页面，查看完整展示卡和可阅读的个人资料；小说正文已发布三章：[第一章《交班以后》](https://sdltf.github.io/jiuyu-shoujie/chapters/001.html)、[第二章《春水不回头》](https://sdltf.github.io/jiuyu-shoujie/chapters/002.html)、[第三章《鱼汤还热着》](https://sdltf.github.io/jiuyu-shoujie/chapters/003.html)。

创作大纲单独保存于 `content/outline.md`，包含完整剧情与结局。网站保留大纲页面与地址，但首页、导航、页脚和其他公开页面都不提供大纲入口，大纲页面不设置展开开关。直接知道地址的人仍可访问；这不是访问权限控制。

## 内容与网站

- `content/characters.json`：人物清单、头像显示位置和个人资料。个人资料取自已有绘制说明，三岛使用最新版本。
- `assets/originals/`：28 张原始人物展示卡 PNG 图片；`28-generation.json` 保存环的展示卡提示词、画风参考和原生尺寸。
- `content/outline.md`：故事大纲（含剧透）。
- `content/chapters/`：小说正文，使用 Markdown 编写。
- `docs/`：已经生成的静态网站，GitHub Pages 从这里发布。
- `scripts/build.py`：将内容生成网页，并为人物图片生成 WebP 浏览版本与头像预览。头像通过 CSS 显示展示卡中间的肖像，不改动原图。

人物图集的手机布局为两列头像；人物详情使用纵向布局，展示卡可以放大并滑动查看，个人资料以网页文字排版。样式和脚本使用内容版本号，发布后不会继续使用旧版本缓存。

首页保留三张错落人物图，28 位人物组成 10 组手动轮播，支持按钮、键盘方向键和手机横向滑动；末组循环补入前面的角色，保持三张构图。点击人物图进入资料页。人物数量随内容清单自动更新。人物图集顶部提供明确的“返回世界观”入口。

轮播使用 `content/characters.json` 中的 `hero_framing` 为每张原图定位头部中心；小屏幕限制放大比例以容纳完整头部，余下空间由柔化背景衔接。展示卡原图不变。

每位角色另有一张专属场景大图，作为人物页的背景与顶部主视觉。桌面显示横幅，手机显示围绕人物调整的竖屏版本；文字在独立暗色区域阅读，页面提供大图放大和原始 PNG 入口。

- `assets/character-backgrounds/01.png` 至 `28.png`：以相应原始展示卡为身份参考，由内置 image_gen 分别生成的场景插画。
- `assets/character-backgrounds/generation-prompts.json`：28 张图片的完整提示词、参考图、原生尺寸、校验值及手机构图中心 `focus_x`。
- `docs/assets/character-backgrounds/`：网站使用的 WebP 图片及 `-mobile.webp` 竖屏版本。场景仅用于视觉氛围，不补充剧情事实。

## 世界档案与视觉素材

`world/` 是独立的世界观与术语 Wiki，现收录 106 条词条，支持搜索、分类、相关词条跳转和人物链接。79 条基础设定默认可读；27 条进阶设定包含后续机制和剧情，必须主动展开才会进入列表和搜索结果。新增环、化形、无法撒谎、耶梦加得、活体边界、循环身体和边界伤口，并衔接既有门路与校准规则。

环首次出场安排在正文第五章，属于第一卷第二剧情单元的旅店日常；前四章不加客串。`content/outline.md` 与当前深化稿同步，并补入其主线、边界规则和阶段安排。四十八个主要剧情单元、二十七站分授与四十九次回流期限保留，局部边界受伤和本体死亡分别处理；大纲继续不提供公开网页入口。

- `content/world.json`：世界速览、分类与术语解释；词条可设置别名、相关词条、相关人物、资料依据和剧透标记。
- `assets/backgrounds/`：原创背景图及完整生成提示词。首页使用“暮色灰桥”，档案页使用“月光档案馆”；由 OpenAI 内置 image_gen 生成。
- `assets/fonts/`：来自 Google Fonts 的 Ma Shan Zheng 和 Noto Sans SC 原字体及 SIL OFL 许可。标题使用手写字形，资料与正文使用黑体。
- `scripts/design_assets.py`：生成桌面与手机 WebP 背景，按网站全部内容裁剪 WOFF2 字体，并保留版权信息与许可。字体由本站提供，无需访问外部字体服务。添加章节后重新构建即可加入新字。

字体原始来源：[Ma Shan Zheng](https://github.com/google/fonts/tree/main/ofl/mashanzheng)、[Noto Sans SC](https://github.com/google/fonts/tree/main/ofl/notosanssc)。网站使用的子集字库命名为 Jiuyu Script 和 Jiuyu Text。

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
