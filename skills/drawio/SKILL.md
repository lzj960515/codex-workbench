---
name: drawio
description: 使用 draw.io 创建、阅读、修改和检查架构图、流程图与系统关系图，并将 `.drawio` 源文件可靠导出为适合 README、PPT 和分享的 PNG。用户说用 drawio 画图、把已有 Mermaid 迁移到 draw.io、编辑现有 `.drawio`、读取带源图的 PNG、同步源图与导出图片，或诊断 draw.io 导出问题时使用。核心结构是节点之间的连接、方向、边界、时序和异常路径；围绕中心主题进行发散、分类和层级整理时使用 mindmap。新图默认以程序员技术草图风格原生绘制。
compatibility: Requires draw.io Desktop with the `drawio` command on PATH; verified on macOS.
---

# Draw.io

## 交付契约

把 `.drawio` 作为权威源文件，把同名 `.png` 作为可再生发布物。创建或修改图时默认同时交付两者，并让它们位于同一目录：

```text
docs/architecture/system-context.drawio
docs/architecture/system-context.png
```

新图默认使用程序员技术草图：自然手绘边框、清楚的深色箭头、克制的斜线填充、纸张色背景和充足留白。草图感来自 draw.io 原生 Rough.js 样式，所有节点和连线仍然是独立、可编辑的图元。

PNG 默认使用浅色主题、24 像素边距、2 倍缩放，并嵌入源图信息。只读任务保持文件不变。简单 Mermaid 已经满足维护和分享需求时保留 Mermaid；需要稳定图片、手动精修或跨工具分享时交付 draw.io 与 PNG。

下文的 `$DRAWIO_SKILL_DIR` 指包含本 `SKILL.md` 的目录。执行脚本前根据当前加载的 Skill 路径设置它，不依赖固定用户名或安装目录。

## 工作流

### 1. 确认图的故事

先阅读用户说明、相关代码、文档、现有 Mermaid、`.drawio` 和图片。明确：

- 图要回答的一个核心问题。
- 主要读者和投放位置，例如 README、PPT 或评审材料。
- 必须出现的节点、分组、连接、方向和异常路径。
- 仓库已有的文档目录、命名方式和视觉规范。

一张图表达一个层级。复杂系统拆成上下文图、容器图或关键流程图，让每张图保持清楚的阅读路径。

### 2. 选择创作路径

| 情况 | 路径 |
| --- | --- |
| 根据文字、代码或设计讨论创建新图 | 从技术草图模板开始，直接编写原生、未压缩 draw.io XML |
| 已有 `.drawio` | 先运行 `inspect_diagram.py`，沿用现有结构；用户要求统一风格时应用技术草图规范 |
| 用户要求迁移已有 Mermaid | 用 `mermaid_to_drawio.py` 保留拓扑，再按技术草图规范重新布局和设定样式 |
| Mermaid 已满足临时文档需要 | 保留 Mermaid，直接交付 Markdown |
| 只有带源图的 PNG | 用 `inspect_diagram.py` 读取并恢复 `.drawio` |
| 只有普通 PNG | 视觉阅读图片，并以它为参考重建新的草图源文件 |

Mermaid 转换是兼容已有文档的迁移能力。新图直接原生绘制，让布局、线条、箭头和视觉层级从一开始服务于最终读者。

### 3. 原生绘制技术草图

完整读取 `references/authoring-guide.md`。从已验证模板开始：

```bash
cp "$DRAWIO_SKILL_DIR/assets/technical-sketch-template.drawio" \
  path/to/diagram.drawio
```

把模板中的示例内容重构为当前业务图，保留已验证的草图参数和连线参数。源文件使用未压缩 XML，便于审查、差异比较和精确修改。

所有可见节点和连线应用 `sketch=1;curveFitting=1;jiggle=2;`。业务节点使用浅色 hachure 手绘填充，主连线使用深色、2.5 像素描边和完整箭头。分组边界保持轻、稀疏，让业务节点成为视觉主体。

修改现有图时保留未涉及的页面、节点 ID 和业务语义。新增 ID 在整个文件内唯一；边的 `source` 与 `target` 指向实际业务节点。标签中的 XML 特殊字符使用实体编码。

图中使用稳定的业务名称和可信本地资源，所有内容都适合进入目标仓库。

### 4. 迁移已有 Mermaid

```bash
python3 "$DRAWIO_SKILL_DIR/scripts/mermaid_to_drawio.py" \
  path/to/flow.mmd path/to/flow.drawio
```

转换结果中的节点和连线是原生、可单独选中的 draw.io 元素。转换完成后继续执行技术草图重构：统一字体和颜色，增加留白，重排节点，把短连接改成长而清楚的连接，并逐条检查箭头。最终 PNG 体现技术草图规范，而不是 Mermaid 默认主题。

### 5. 读取与检查结构

```bash
python3 "$DRAWIO_SKILL_DIR/scripts/inspect_diagram.py" path/to/diagram.drawio
python3 "$DRAWIO_SKILL_DIR/scripts/inspect_diagram.py" path/to/diagram.png
```

检查器输出页面、节点、分组、连接、标签、坐标和 PNG 嵌入信息。结构语义以源 XML 为准，视觉结果以渲染图片为准。

从带源图的 PNG 恢复可编辑文件：

```bash
python3 "$DRAWIO_SKILL_DIR/scripts/inspect_diagram.py" \
  path/to/diagram.png --extract path/to/diagram.drawio
```

只读解释按以下顺序组织：图的范围、页面/分组、关键节点、主要连接、主流程、异常或回路、无法从图中确认的业务含义。

### 6. 导出 PNG

```bash
python3 "$DRAWIO_SKILL_DIR/scripts/export_png.py" \
  path/to/diagram.drawio path/to/diagram.png
```

README 或普通演示文稿使用默认参数。固定宽度使用 `--width 1600`；透明背景使用 `--transparent`；多页面图使用 `--page <1-based-index>` 分别导出。

脚本先写临时文件，验证 PNG 签名、像素尺寸和嵌入源图信息，再原子替换目标文件。

### 7. 视觉验收

每次导出后实际查看 PNG，并在原尺寸和约 50% 缩放下检查：

- 所有主要框和连线都呈现一致的手绘笔触，图像像程序员白板草图而不是 UI 卡片集合。
- 每条业务连线都有连续、可见的线段；箭头完整露出，与目标框之间边界清楚。
- 边标签位于线条上方或侧面，标签两侧各保留可见线段，标签背景只覆盖文字需要的范围。
- 连线连接业务节点，分组边界保持装饰职责；正交转弯、分支和回路都能一眼追踪。
- 文字完整清晰，节点尺寸覆盖标签，中文与英文在 README 缩放后仍可读。
- 颜色表达稳定语义，浅色手绘填充和深色线条形成足够对比。
- 节点保持自然但有秩序的对齐，主路径拥有充足留白，连接尽量减少交叉。

视觉结果未达到这些标准时，回到源图调整几何位置、边路由或样式，再重新导出和查看。XML 可解析和命令成功只证明文件有效，视觉验收决定图是否完成。

## 修改与同步

源文件发生实质变化后重新导出 PNG。更新 README 时使用仓库相对路径：

```markdown
![系统架构](docs/architecture/system-context.png)
```

回复中给出 `.drawio` 与 PNG 的绝对路径、PNG 尺寸、导出主题和主要阅读顺序。只读任务说明读取了源图、嵌入 PNG 还是普通图片。

## 失败处理

- `drawio` 不可用：报告依赖缺失；macOS 使用 `brew install --cask drawio` 安装官方桌面版。
- XML 无效：定位解析错误，修正源文件后再导出。
- PNG 没有嵌入源图：读取相邻 `.drawio`；两者都没有时按图片重建。
- 线条或箭头不清楚：增加节点间距，把标签移到线外，设置 `endSize=18`，让连接指向业务节点并重新检查路由。
- 导出空白或裁切：检查节点几何尺寸、页面索引、隐藏图层与画布边界。
- 字体或外部图片缺失：使用本机可用字体或仓库内资源，保持离线导出一致。
