# 九域守界

九域守界的人物设定图集与小说阅读网站。

**访问网站：[sdltf.github.io/jiuyu-shoujie](https://sdltf.github.io/jiuyu-shoujie/)**

[印象图画廊](https://sdltf.github.io/jiuyu-shoujie/art/)集中展示全部章节插画，保留完整构图，支持按章节筛选、放大切换、查看原始 PNG，以及跳转至对应正文场景。首页、主导航和正文页均提供画廊入口。画廊由 `content/chapter-art.json` 自动生成，后续新增配图会随网站构建一起收录。

[二创页面](https://sdltf.github.io/jiuyu-shoujie/fanworks/)收录粉丝的图片与文字作品，支持分类筛选、搜索、图片放大和长文字展开阅读。作品由站主收集后更新，每件作品保留创作者署名和描述。目前收录酥心糖的两张图片二创，描述分别为“神秘东方三人组”和“上课太无聊了于是嬷了三岛”，保留用户提供的完整 JPEG、PNG 原图。

目前收录 28 位角色，新增[环（张瑞康）](https://sdltf.github.io/jiuyu-shoujie/gallery/28.html)。人物列表显示头像，点击后进入独立人物页面，查看完整展示卡和可阅读的个人资料；小说正文已发布十章：[第一章《交班以后》](https://sdltf.github.io/jiuyu-shoujie/chapters/001.html)、[第二章《春水不回头》](https://sdltf.github.io/jiuyu-shoujie/chapters/002.html)、[第三章《鱼汤还热着》](https://sdltf.github.io/jiuyu-shoujie/chapters/003.html)、[第四章《人已经出来了》](https://sdltf.github.io/jiuyu-shoujie/chapters/004.html)、[第五章《不回答的客人》](https://sdltf.github.io/jiuyu-shoujie/chapters/005.html)、[第六章《绳子的另一头》](https://sdltf.github.io/jiuyu-shoujie/chapters/006.html)、[第七章《早钟以后》](https://sdltf.github.io/jiuyu-shoujie/chapters/007.html)、[第八章《井壁上的旧纹》](https://sdltf.github.io/jiuyu-shoujie/chapters/008.html)、[第九章《石碑指向的地方》](https://sdltf.github.io/jiuyu-shoujie/chapters/009.html)、[第十章《水往河里走》](https://sdltf.github.io/jiuyu-shoujie/chapters/010.html)。

创作大纲单独保存于 `content/outline.md`，包含完整剧情与结局。网站保留大纲页面与地址，但首页、导航、页脚和其他公开页面都不提供大纲入口，大纲页面不设置展开开关。直接知道地址的人仍可访问；这不是访问权限控制。

## 内容与网站

- `content/characters.json`：人物清单、独立头像文件和个人资料。个人资料取自已有绘制说明，三岛使用最新版本。
- `assets/originals/`：28 张原始人物展示卡 PNG 图片；`28-generation.json` 保存环的展示卡提示词、画风参考和原生尺寸。
- `content/outline.md`：故事大纲（含剧透）。
- `content/chapters/`：小说正文，使用 Markdown 编写。
- `content/chapter-art.json`：章节印象图与插入位置。按 `A-B` 编号，以对应正文段落作为定位；正文原稿无需添加图片标签。
- `assets/chapter-art/`：第一至第十章使用用户提供的十八张原始 PNG，第七章三张、第八至第十章各两张，按提供顺序插入。先前生成稿保存在 `archive/`，提示词及原参考路径保存在 `generation-prompts.json`。网页保留完整构图，可点击放大；目录使用各章第一张图作缩略图。
- `docs/assets/chapter-art/`：网站使用的完整、960 像素和 480 像素 WebP 版本；手机根据屏幕宽度加载合适版本。
- `docs/`：已经生成的静态网站，GitHub Pages 从这里发布。
- `scripts/build.py`：将内容生成网页，并为人物图片生成 WebP 浏览版本。图集和人物页的头像使用独立绘制的方形画像，保留完整头部构图。

人物图集的手机布局为两列头像；人物详情使用纵向布局，展示卡可以放大并滑动查看，个人资料以网页文字排版。样式和脚本使用内容版本号，发布后不会继续使用旧版本缓存。

每位角色的档案包含人物展示卡、专属场景背景、独立人物头像和网页个人资料。人物页提供头像与背景的查看按钮及原始 PNG 入口，放大查看时可在三种图片之间切换。

- `assets/avatars/01.png` 至 `28.png`：参考各自展示卡，由内置 image_gen 单独绘制的高清方形头像，保留原生 PNG。
- `assets/avatars/generation-prompts.json`：完整生成提示词、身份参考、原生尺寸及校验值。
- `docs/assets/avatars/`：1024 像素放大图、512 像素与 256 像素响应式 WebP，图集按屏幕尺寸加载。头像由独立图片呈现，不从展示卡中裁取。

人物图集与 28 位角色详情页均提供“原版 / Q版”头像开关，默认使用原版。浏览器会记住选择，刷新、进入人物页及返回图集时继续使用所选风格；头像放大按钮和原图链接也随选择切换。

- `assets/chibi-avatars/01.png` 至 `28.png`：28 张独立绘制的 Q 版头肩头像，保留透明背景及原生 PNG。
- `assets/chibi-avatars/generation-prompts.json`：Q 版头像的生成提示词、角色对应关系、原生尺寸和校验值。
- `docs/assets/chibi-avatars/`：保留透明背景的 1024、512 与 256 像素 WebP，按屏幕尺寸加载。

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

### 收录二创

在 `content/fanworks.json` 的 `works` 数组中添加作品，按数组顺序展示。`id` 使用唯一的小写字母、数字和连字符；`type` 为 `image` 或 `text`。两类作品都必须有 `creator`（创作者）和 `description`（描述），`title`（标题）可选。图片类填写 `image`，文字类填写 `text`，文字中的换行会原样保留。

以下为字段示例，示例作品不发布到页面：

```json
{
  "works": [
    {
      "id": "001",
      "type": "image",
      "image": "assets/fanworks/001.jpg",
      "creator": "酥心糖",
      "description": "神秘东方三人组"
    },
    {
      "id": "002",
      "type": "text",
      "text": "在这里填写作品正文。\n\n在这里继续下一段。",
      "creator": "创作者署名",
      "description": "作品描述"
    }
  ]
}
```

图片放在 `assets/fanworks/`，支持 PNG、JPEG、WebP 和 GIF。构建会将原图复制到网站，为静态图片生成保留完整构图的响应式 WebP；动图保留原文件播放。文字作为纯文本显示，不解析 HTML。收录后执行下面的构建与发布步骤即可。

### 构建与发布

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
