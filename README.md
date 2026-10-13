# 九域守界

九域守界的人物设定图集与小说阅读网站。

**访问网站：[sdltf.github.io/jiuyu-shoujie](https://sdltf.github.io/jiuyu-shoujie/)**

[印象图画廊](https://sdltf.github.io/jiuyu-shoujie/art/)集中展示全部章节插画，保留完整构图，支持按章节筛选、放大切换、查看原始 PNG，以及跳转至对应正文场景。首页、主导航和正文页均提供画廊入口。画廊由 `content/chapter-art.json` 自动生成，后续新增配图会随网站构建一起收录。

[二创页面](https://sdltf.github.io/jiuyu-shoujie/fanworks/)收录粉丝的图片与文字作品，支持分类筛选、搜索、图片放大和长文字展开阅读。作品由站主收集后更新，每件作品保留创作者署名和描述。目前共二十三件图片作品：酥心糖的两张投稿，署名【三岛（CodeX）】的九张二创，以及琉西法（Codex）的十二张非正篇 CP 插画。包括三岛与土方奏一的三张同人图、赵香香与谢寄风的酒馆追逐腿部修正版，以及林清翊与乐温的五张伙伴日常与冒险图；林清翊保留原设13岁外观，成年屋顶稿未收录。非正篇 CP 插画按四组三张的原始编号顺序收录：小语与韦侃、闵霁与曲柯、三岛与土方奏一，以及酥心糖、楚惊殊、单谣；每张保留标题、署名、完整简介和非正篇关系说明。全部作品保留完整原图。

目前收录 28 位角色，新增[环（张瑞康）](https://sdltf.github.io/jiuyu-shoujie/gallery/28.html)。人物列表显示头像，点击后进入独立人物页面，查看完整展示卡和可阅读的个人资料；小说正文已发布十六章：[第一章《交班以后》](https://sdltf.github.io/jiuyu-shoujie/chapters/001.html)、[第二章《春水不回头》](https://sdltf.github.io/jiuyu-shoujie/chapters/002.html)、[第三章《鱼汤还热着》](https://sdltf.github.io/jiuyu-shoujie/chapters/003.html)、[第四章《人已经出来了》](https://sdltf.github.io/jiuyu-shoujie/chapters/004.html)、[第五章《不回答的客人》](https://sdltf.github.io/jiuyu-shoujie/chapters/005.html)、[第六章《绳子的另一头》](https://sdltf.github.io/jiuyu-shoujie/chapters/006.html)、[第七章《早钟以后》](https://sdltf.github.io/jiuyu-shoujie/chapters/007.html)、[第八章《井壁上的旧纹》](https://sdltf.github.io/jiuyu-shoujie/chapters/008.html)、[第九章《石碑指向的地方》](https://sdltf.github.io/jiuyu-shoujie/chapters/009.html)、[第十章《水往河里走》](https://sdltf.github.io/jiuyu-shoujie/chapters/010.html)、[第十一章《井边的第一桶水》](https://sdltf.github.io/jiuyu-shoujie/chapters/011.html)、[第十二章《平安二字》](https://sdltf.github.io/jiuyu-shoujie/chapters/012.html)、[第十三章《墙后的脉动》](https://sdltf.github.io/jiuyu-shoujie/chapters/013.html)、[第十四章《还不能走》](https://sdltf.github.io/jiuyu-shoujie/chapters/014.html)、[第十五章《留下的水》](https://sdltf.github.io/jiuyu-shoujie/chapters/015.html)、[第十六章《再走一程》](https://sdltf.github.io/jiuyu-shoujie/chapters/016.html)。

创作大纲单独保存于 `content/outline.md`，包含完整剧情与结局。网站保留大纲页面与地址，但首页、导航、页脚和其他公开页面都不提供大纲入口，大纲页面不设置展开开关。直接知道地址的人仍可访问；这不是访问权限控制。

## 内容与网站

- `content/characters.json`：人物清单、独立头像文件和个人资料。个人资料取自已有绘制说明，三岛使用最新版本。
- `assets/originals/`：28 张原始人物展示卡 PNG 图片；`28-generation.json` 保存环的展示卡提示词、画风参考和原生尺寸。
- `content/outline.md`：故事大纲（含剧透）。
- `content/chapters/`：小说正文，使用 Markdown 编写。
- `content/chapter-art.json`：章节印象图与插入位置。按 `A-B` 编号，以对应正文段落作为定位；正文原稿无需添加图片标签。
- `assets/chapter-art/`：第一至第十章使用用户提供的十八张原始 PNG，第七章三张、第八至第十章各两张，按提供顺序插入。第十一至十六章每章两张由内置 image_gen 绘制，提示词与参考图分别记录在 `chapter11-12-generation.json`、`chapter13-14-generation.json` 和 `chapter15-16-generation.json`。先前生成稿保存在 `archive/`，提示词及原参考路径保存在 `generation-prompts.json`。网页保留完整构图，可点击放大；目录使用各章第一张图作缩略图。
- `docs/assets/chapter-art/`：网站使用的完整、960 像素和 480 像素 WebP 版本；手机根据屏幕宽度加载合适版本。
- `docs/`：已经生成的静态网站，GitHub Pages 从这里发布。
- `scripts/build.py`：将内容生成网页，并为人物图片生成 WebP 浏览版本。图集和人物页的头像使用独立绘制的方形画像，保留完整头部构图。

人物图集的手机布局为两列头像；人物详情使用纵向布局，展示卡可以放大并滑动查看，个人资料以网页文字排版。样式和脚本使用内容版本号，发布后不会继续使用旧版本缓存。

每位角色的档案包含原人物展示卡（人设图-1）、叙事人设图-2、横屏战斗壁纸、专属场景背景、独立人物头像、Q版全身立绘、三张表情包和网页个人资料。28 张人设图-2 各有独立的表情、动作与场景；28 张战斗壁纸按各人的能力绘制，含交锋、战场修复与救治。原卡、头像和背景均保留。人物页支持完整构图放大、左右切换、细节缩放与原始 PNG 查看，手机同样保留整幅图片。

- `content/character-art.json`：28 位角色的新插画与壁纸对应关系、标题、描述和原生尺寸；构建时自动收录进各自档案。
- `assets/character-scenes/`：28 张原生 PNG 人设图-2，包括动作与比例修订后的版本；生成提示词保存在 `generation-prompts.json`。
- `assets/character-battles/`：28 张约 16:9 横屏战斗场景 PNG；独立提示词与参考图保存在 `generation-prompts.json`。
- `docs/assets/character-scenes/` 与 `docs/assets/character-battles/`：保留完整构图的原生尺寸、960 与 480 宽 WebP，按屏幕大小加载。插画依据既有设定创作，不补充正文剧情事实。

- `assets/avatars/01.png` 至 `28.png`：参考各自展示卡，由内置 image_gen 单独绘制的高清方形头像，保留原生 PNG。
- `assets/avatars/generation-prompts.json`：完整生成提示词、身份参考、原生尺寸及校验值。
- `docs/assets/avatars/`：1024 像素放大图、512 像素与 256 像素响应式 WebP，图集按屏幕尺寸加载。头像由独立图片呈现，不从展示卡中裁取。

人物图集与 28 位角色详情页均提供“原版头像 / Q版全身”开关，默认使用原版。浏览器会记住选择，刷新、进入人物页及返回图集时继续使用所选风格；放大按钮和原图链接也随选择切换。两种风格使用同一深色底色。

- `assets/chibi-avatars/01.png` 至 `28.png`：重新绘制的28张Q版全身标准立绘，来自新四宫格的左上格，原生627×627透明PNG。
- `assets/chibi-avatars/generation-prompts.json`：角色对应关系、来源四宫格、尺寸和校验值。
- `docs/assets/chibi-avatars/`：保留透明通道的响应式WebP。仅裁去空白边距并缩小，srcset按实际宽度生成，不裁掉身体。
- [Q版全身立绘与表情包](https://sdltf.github.io/jiuyu-shoujie/stickers/)：28位角色的112张独立图，支持搜索、放大、切换和透明PNG下载。人物页同时展示本角色四张图。
- `content/chibi-stickers.json`：28位角色、四种动作、表情说明、源文件路径及SHA-256。
- `assets/chibi-stickers/`：112张独立PNG、28张四宫格、生成与修改提示词，以及完整素材包`complete.zip`（140张PNG与3份说明，143个文件）。四宫格原生1254×1254，独立图直接四等分裁切，未放大伪称2048像素。
- `docs/assets/chibi-stickers/`：网页使用的完整姿态与256像素WebP预览，深色背景为`#24323d`。

首页保留三张错落人物图，28 位人物组成 10 组手动轮播，支持按钮、键盘方向键和手机横向滑动；末组循环补入前面的角色，保持三张构图。点击人物图进入资料页。人物数量随内容清单自动更新。人物图集顶部提供明确的“返回世界观”入口。

轮播使用 `content/characters.json` 中的 `hero_framing` 为每张原图定位头部中心；小屏幕限制放大比例以容纳完整头部，余下空间由柔化背景衔接。展示卡原图不变。

每位角色另有一张专属场景大图，作为人物页的背景与顶部主视觉。“背景切换”让角色大图与战斗图使用同一整幅背景区域、相同的铺满方式和文字遮罩，以同等地位轮换。每 12 秒自动切换，以 1.6 秒淡入淡出衔接，也可用按钮或方向键手动切换、暂停；暂停选择会随浏览器记住。手机背景依据各图的角色位置取景，战斗图的取景位置由 `content/character-art.json` 的 `background_focus_x` 控制；点击“查看当前大图”仍可查看完整构图。文字保持稳定，当前大图和背景原图的链接随背景切换。减少动态的系统设置默认暂停轮换；切出页面、主视觉离开屏幕、操作切换按钮或打开图片查看器时暂缓自动播放。后续图片按需加载，加载失败保留当前画面。未启用 JavaScript 时仍展示原专属场景。

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

`tags` 为不重复的字符串数组，用于角色、CP或人物组合、主题及明确的创作设定；使用统一名称，例如 `三岛`、`三岛 × 土方奏一`、`日常`、`非正篇`。标签不得为空或带首尾空格。现有28件作品均已补齐标签；未来作品可省略此字段，兼容已有收录格式。页面自动生成多行标签索引与每个标签的作品数量，所有标签随屏幕宽度换行，直接点击即可筛选，作品卡片也展示可点击标签。标签、图片／文字分类和关键词搜索取交集；再次点击当前标签或点击“全部标签”可取消标签筛选。当前标签保存在网页地址的 `tag` 参数中，复制链接或刷新可保留标签选择。原有标题、署名、描述与原图保留。

以下为字段示例，示例作品不发布到页面：

```json
{
  "works": [
    {
      "id": "001",
      "type": "image",
      "image": "assets/fanworks/001.jpg",
      "creator": "酥心糖",
      "description": "神秘东方三人组",
      "tags": ["酥心糖", "楚惊殊", "单谣", "群像", "手绘"]
    },
    {
      "id": "002",
      "type": "text",
      "text": "在这里填写作品正文。\n\n在这里继续下一段。",
      "creator": "创作者署名",
      "description": "作品描述",
      "tags": ["三岛", "日常"]
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
