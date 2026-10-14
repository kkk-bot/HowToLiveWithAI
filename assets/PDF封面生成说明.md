# PDF 竖版封面

成品：[普通人的 AI 学习指南 PDF 竖版封面 v1](普通人的AI学习指南-PDF竖版封面-v1.png)。GitHub 首页继续使用[横版封面 v5](普通人的AI学习指南-封面-v5.png)。

2026-10-14 使用内置 image_gen 工具，将既有蓝白桌面封面重新组织为 A4 竖版构图。生成尺寸 1054 × 1492，与 A4 比例差小于 0.1%。PDF 等比完整显示，页面边缘只有不足 0.3 pt 的适配间隙，不拉伸、不裁切。

标题、副标题、说明、四个卡片与底部提示逐项核对；原横版文件保留。新版用于修复将横幅居中贴在竖页上造成的大面积留白，不修改正文内容。

完整生成提示词：

```text
Use case: compositing / cover re-layout.
Asset type: final flat portrait A4 front cover artwork for an existing Chinese PDF guide.
Input image 1 is the EDIT TARGET and defines the approved content, illustration objects, black/cobalt typography and cool blue-white palette.
Primary request: transform the landscape cover into a beautifully composed full-page PORTRAIT cover, aspect ratio exactly 210:297, ideally 1536x2176 or nearest A4 portrait resolution. Reflow the complete design, not a landscape rectangle pasted into a portrait canvas. No letterboxing, no giant top/bottom blank bands. Artwork and pale blue-white desk background extend to all four edges.

Preserve the existing title, wording, four information-card labels, blue-white desk illustration style, original brand HowToLiveWithAI. Main title must NOT include 与行动. Reposition and resize the existing objects and text to suit the tall page. Do not just stretch or crop the original landscape poster.

Composition: brand and thin rule at the top with a small normal safe margin; huge bold black and cobalt title across the upper quarter, using two or three natural lines that read exactly 普通人的 AI 学习指南. Bold subtitle immediately below, black and highly readable. Supporting copy below that. A beautifully detailed cool-white/blue desk with the silver-blue laptop showing abstract chat and a simple branching diagram, notebook, cobalt pen, checklist papers, blue ceramic mug fills the lower portion and right area, integrated naturally with text rather than competing. The four readable rounded blue/mint information cards can be a 2x2 block in the middle/lower-left, away from the illustration's busy details. Small gray learning-reference note near bottom. Use intentional generous text breathing space, but the page must read as one continuous finished portrait book cover. Keep all copy safely inset; no cropped Chinese characters. Crisp typography, soft natural daylight, thoughtful ordinary learning mood.

Text verbatim, all in simplified Chinese, no invented extra words:
Brand: "HowToLiveWithAI"
Main title: "普通人的 AI 学习指南"
Subtitle line 1: "认识 AI，减少焦虑"
Subtitle line 2: "学会判断，从小事开始行动"
Supporting text: "学什么、怎么用、怎样开始"
Supporting text: "从真实问题练习提问、核查与判断"
Audience: "面向学生、初入职场与寻找方向的年轻人"
Card 1: "6章主线" / "系统入门"
Card 2: "29节正文" / "循序阅读"
Card 3: "基础教学" / "提问与核查"
Card 4: "判断与边界" / "保留自主选择"
Bottom note: "仅供学习参考，请结合实际情况判断"

Constraints: PORTRAIT A4, full page composition. No new theme, no change of main title, no subtitle removal, no income claims, no robots, no people, no cafe, no beige/teal old cover, no watermark, no book mockup or 3D book, no external border. Preserve original content and approved visual language while reorganizing the layout for a tall page.
```
