---
name: mindmap
description: 把想法、文档、代码和讨论整理为可编辑的草图思维导图，并读取、修改或导出 `.drawio` 与带源图的 PNG。用户说画思维导图、脑图、mind map、mindmap，把文章或需求整理成分支，增加或调整分支，解释已有思维导图，或判断内容更适合思维导图还是架构图时使用。核心是主题发散、分类和层级；流程、调用、部署和系统关系图交给 drawio。任务同时包含主题发散和关键流程时，先创建思维导图，再使用 drawio 创建独立流程图。
compatibility: Requires the shared drawio Skill and draw.io Desktop with the `drawio` command on PATH; verified on macOS.
---

# Mindmap

## 交付契约

把材料整理成一张可以继续思考、手工精修和稳定分享的思维导图。`.drawio` 是权威源文件，同名 `.png` 是可再生发布物；新建或实质修改后默认同时交付：

```text
docs/mindmaps/social-analysis.drawio
docs/mindmaps/social-analysis.png
```

PNG 使用浅色主题、24 像素边距、2 倍缩放并嵌入完整源图。源图保持未压缩 XML，所有主题都是原生、可单独编辑的 draw.io 图元。

新图默认使用程序员白板草图：温暖纸张色、Rough.js 手绘笔触、清楚的中心主题、按一级分支延续的克制配色、自然曲线和充足留白。层级归属使用无箭头分支线；非层级且具有方向的语义关系使用虚线箭头。

下文的 `$MINDMAP_SKILL_DIR` 指本 Skill 目录，`$DRAWIO_SKILL_DIR` 指已加载的 drawio Skill 目录。执行脚本前根据当前加载的 Skill 路径设置它们，不依赖固定用户名或安装目录。

## 1. 判断图的类型

思维导图围绕一个中心主题组织发散、分类和层级。以下任务直接进入本工作流：

- 梳理一个主题包含哪些方面。
- 把文章、会议记录、需求或代码知识整理成层级。
- 进行头脑风暴、方案空间探索或学习笔记归纳。
- 修改现有脑图的分支、顺序、层级或重点。

当核心问题是先后顺序、服务调用、数据流、部署边界、状态转换或异常路径时，使用 drawio Skill 创建架构图或流程图。材料同时包含两类问题时，先用思维导图建立问题空间，再为关键流程创建独立 draw.io 图。

## 2. 组织内容

阅读用户材料、相关代码和已有图，先确定中心问题和主要读者。完整读取 `references/authoring-guide.md`，再设计：

- 一个能够概括整张图的中心主题。
- 彼此平行、含义清楚的一级分支。
- 从概念到细节逐层展开的子主题。
- 需要突出、折叠、拆图或改用关系图的内容。

重组信息并提炼原文。节点使用短语表达一个概念；详细证据、长说明和代码保留在原文或相邻文档中。

用户要求整理具体事件或文档但没有提供材料时，先读取任务范围内可以获得的来源。仍缺少事实时交付一张明确标记为模板的可填写结构，用问题或占位主题表达所需信息，同时说明没有推断具体事实；需要形成事实性总结时向用户指出缺少的来源。

## 3. 创建原生思维导图

先查看 `assets/mindmap-sketch-template.png`，把它作为草图笔触、层级重量、分支曲线和留白的视觉基线。对应的 `assets/mindmap-sketch-template.drawio` 是可编辑参考源图。

在目标项目的 `tmp/` 下创建一次性 JSON 大纲，然后运行原生绘制脚本：

```json
{
  "title": "社交内容分析",
  "layout": "both",
  "branches": [
    {
      "text": "输入",
      "children": [
        {"text": "账号"},
        {"text": "关键词"}
      ]
    },
    {
      "text": "处理",
      "children": [
        {"text": "采集"},
        {"text": "分析"}
      ]
    }
  ]
}
```

```bash
python3 "$MINDMAP_SKILL_DIR/scripts/create_mindmap.py" \
  path/to/outline.json path/to/topic.drawio
```

`layout` 支持 `both`、`right` 和 `left`。一级分支可以显式设置 `"side": "left"` 或 `"side": "right"`；`color` 支持 `blue`、`yellow`、`green`、`red`、`violet` 和 `orange`。

脚本生成原生、未压缩且可编辑的 draw.io 初稿。生成后把一次性 JSON 留在 `tmp/`，把 `.drawio` 作为唯一权威源文件。把自动排版作为可编辑起点，根据实际内容继续调整节点位置、分支顺序、文字宽度和配色，让布局服务于当前主题。

Markdown、列表或已有 Mermaid 可以作为内容输入。先重新判断一级分支和层级，再生成原生思维导图；转换只继承有价值的内容结构。

## 4. 读取与解释

读取 `.drawio` 或带源图的 PNG：

```bash
python3 "$MINDMAP_SKILL_DIR/scripts/inspect_mindmap.py" \
  path/to/topic.drawio --format markdown

python3 "$MINDMAP_SKILL_DIR/scripts/inspect_mindmap.py" \
  path/to/topic.png --format json
```

检查器复用 drawio Skill 的嵌入源图读取能力，并按连接关系恢复中心主题、分支层级和跨分支连接。解释时依次说明中心问题、一级分支、关键子主题、突出关系和图中无法确认的业务含义。

从 PNG 恢复源文件：

```bash
python3 "$DRAWIO_SKILL_DIR/scripts/inspect_diagram.py" \
  path/to/topic.png --extract path/to/topic.drawio
```

普通 PNG 没有嵌入源图时，视觉阅读图片并重建新的可编辑源文件，同时说明重建边界。

## 5. 修改现有思维导图

先运行 `inspect_mindmap.py` 理解完整层级，再运行 drawio Skill 的 `inspect_diagram.py` 检查节点 ID、边端点和几何位置，并实际查看最终 PNG。修改时保持未涉及的页面、节点 ID、分支语义和手工位置；新增节点使用唯一、可读的 ID，并让层级边的 `source` 与 `target` 指向真实主题节点。

内容变化按思维过程处理：新增概念放入最贴近的稳定分支，改变分类时移动整个子树，删除节点前确认其子主题的归属。窄范围修改优先保留原有几何位置，先利用可读的空白区域；空间不足时只重排最小受影响子树，让其他分支保持稳定。

同级主题的源连接顺序表达阅读顺序，并与图中从上到下的视觉顺序保持一致。插入或移动节点时同时调整 XML 元素、层级边顺序和几何位置。

源文件变化后重新导出 PNG。已有 PNG 可读时沿用它的像素宽度、主题和透明背景设置；新图或缺少旧发布物时使用默认导出参数。

## 6. 导出与视觉验收

```bash
python3 "$DRAWIO_SKILL_DIR/scripts/export_png.py" \
  path/to/topic.drawio path/to/topic.png
```

每次导出后实际查看 PNG，并在原尺寸和约 50% 缩放下检查：

- 中心主题是第一视觉焦点，一级分支可以快速扫读。
- 同一一级分支沿用稳定颜色，颜色数量克制且对比充足。
- 曲线连续可见，进入节点前有清楚的线段，文字不压住分支线。
- 层级分支保持无箭头，虚线箭头只表达具有明确方向的非层级关系。
- 根、一级分支和叶节点的视觉重量逐级降低，不呈现为整齐堆叠的 UI 卡片。
- 双向布局保持左右重量平衡；单向布局保持从中心到细节的顺畅阅读路径。
- 节点之间有足够留白，中文、英文和代码标识符在 README 缩放后仍清楚。
- 所有业务图元使用一致的手绘笔触，最终结果像整理过的程序员白板。

未达到标准时回到源图调整几何位置、分支曲线和文字尺寸，再重新导出并查看。命令成功只证明文件有效，视觉验收决定图是否完成。

完成视觉检查后运行交付校验，统一验证中心主题、层级结构、PNG 嵌入信息以及 PNG 与权威源图同步状态：

```bash
python3 "$MINDMAP_SKILL_DIR/scripts/validate_mindmap.py" \
  path/to/topic.drawio path/to/topic.png
```

## 7. 回复格式

交付时给出 `.drawio` 与 PNG 的绝对路径、PNG 尺寸、布局方向、中心主题和一级分支阅读顺序。说明已经进行结构检查、嵌入源图检查和视觉检查。只读任务说明读取的是源图、嵌入 PNG 还是普通图片。

## 失败处理

- `drawio` 命令不可用：报告依赖缺失，并使用 `brew install --cask drawio` 安装官方桌面版。
- drawio Skill 不可用：报告组合依赖缺失，保留已经完成的内容大纲和目标路径。
- JSON 无效：根据脚本的字段路径修正标题、分支、子节点、方向或颜色。
- 图过深或过密：按独立问题拆成总览图和细节图，并在父图保留入口主题。
- PNG 没有嵌入源图：读取相邻 `.drawio`；两者都不存在时按图片重建。
- 分支交叉或文字拥挤：调整一级分支侧向、移动完整子树、增加层级间距并重新导出。
