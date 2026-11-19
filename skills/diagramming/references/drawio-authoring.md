# draw.io 制作与工具

本页集中维护流程图、架构图和思维导图共同使用的文件、风格、操作和显示检查。`$DIAGRAM_SKILL_DIR` 指包含本 Skill 的实际目录；按加载路径设置该变量，所有脚本和模板均从此包取得。

## 选择制作路径

| 输入 | 处理 |
| --- | --- |
| 新的流程图或架构图 | 以 `assets/technical-sketch-template.drawio` 为起点直接写原生 XML |
| 新的思维导图 | 阅读 `assets/mindmap-sketch-template.png` 和对应 `.drawio`；按[脑图方法](mindmaps.md)组织大纲并运行生成器 |
| 已有 `.drawio` | 读取结构后就地修改，保留受影响范围外的内容和手工位置 |
| 已有 Mermaid，用户需要 draw.io | 转换拓扑后调整原生图元、样式和布局 |
| 带源图 PNG | 提取 `.drawio` 后继续读取或修改 |
| 普通图片 | 视觉读取，按可确认的内容重建可编辑源图，说明重建范围 |

```bash
cp "$DIAGRAM_SKILL_DIR/assets/technical-sketch-template.drawio" \
  path/to/diagram.drawio

python3 "$DIAGRAM_SKILL_DIR/scripts/mermaid_to_drawio.py" \
  path/to/flow.mmd path/to/flow.drawio
```

转换后的节点和边均可编辑。转换负责继承有价值的结构，后续按读者问题修正内容和布局。业务正确性先于样式细节。

## 共用草图风格

新图使用温暖纸张背景 `#FFFDF5`、深蓝黑文字与主线 `#243142`。所有可见业务图元采用 draw.io 原生 Rough.js：

```text
sketch=1;curveFitting=1;jiggle=2;
```

字体默认 `Chalkboard SE,Comic Sans MS`，中文由系统字体回退；本机字体缺少时选用当前可用字体并检查显示。风格依靠原生边框、填充和连线，继续保持图元独立可编辑。

| 记号色 | 填充 | 流程图常见含义 | 脑图线色 |
| --- | --- | --- | --- |
| blue | `#DCEBFF` | 用户、入口、输入 | `#376A9E` |
| yellow | `#FFF2CC` | 核心动作 | `#9A6B14` |
| green | `#DFF3E4` | 数据、保存、确认结果 | `#3F7D54` |
| red | `#F9DFDF` | 失败、停止、风险 | `#A84B49` |
| violet | `#E9E1F7` | 自动化与辅助能力 | `#76569A` |
| orange | `#FDE7C3` | 说明、重点、待讨论 | `#A8642A` |

流程图按稳定业务语义选少量颜色；脑图按一级分支归属配色。同一图的颜色含义保持一致，文字及连线在浅色背景上有足够对比。

### 流程图与架构图

动作采用圆角矩形，判断采用菱形，数据存储和队列可用圆柱体。分组边界轻、稀疏，表达职责、部署或业务阶段；连接指向实际业务节点。说明便签用橙色墨水 `#D97736`。

节点参考参数：

```text
rounded=1;whiteSpace=wrap;html=1;arcSize=14;
strokeColor=#243142;strokeWidth=2;
hachureGap=8;fillWeight=1.5;
fontFamily=Chalkboard SE,Comic Sans MS;fontSize=18;fontColor=#243142;
```

主连线参考参数：

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;
sketch=1;curveFitting=1;jiggle=2;strokeColor=#243142;strokeWidth=2.5;
endArrow=classic;endFill=1;endSize=18;
fontFamily=Chalkboard SE,Comic Sans MS;fontSize=15;fontColor=#243142;
labelBackgroundColor=#FFFDF5;
```

可选或异步关系用 `dashed=1;dashPattern=8 6;`。水平标签可设置 `offset.y=-16`，垂直标签可设置 `offset.x=40` 至 `64`，让文字位于线外，标签背景只包文字范围。

节点通常宽 170—230、高 72—110，内部留白 16—24，水平间隔 140—220、垂直间隔 110—180；这些是起始尺度，中文长度和画布用途决定最终尺寸。长节点先整理内容，再扩大必要空间。连线标签两侧保留可见线段，箭头在目标框前完整露出。

### 思维导图

中心用较大的手绘椭圆、黄色填充和 26 号粗体；一级分支用 19 号粗体和分支色，二级用浅色填充与 17 号字体，更深层用纸张色或极浅填充与 16 号字体。尺寸随内容调整，保持从中心到细节的视觉层级。

层级线采用自然曲线、分支色与逐级变细描边：

```text
edgeStyle=entityRelationEdgeStyle;curved=1;rounded=1;
sketch=1;curveFitting=1;jiggle=2;startArrow=none;endArrow=none;
```

跨分支关系按实际含义使用带标签虚线箭头，层级关系继续用无箭头曲线。

## 原生 XML 与修改

源文件保持未压缩结构：

```xml
<mxfile host="Agent">
  <diagram id="overview" name="总览">
    <mxGraphModel grid="1" gridSize="10" page="1" pageScale="1"
      pageWidth="1600" pageHeight="1000" background="#FFFDF5">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

业务节点和边采用唯一、可读且稳定的 ID，`source`、`target` 指向实际节点。分组内的 `parent` 指向分组，坐标相对分组计算。标签中的 XML 特殊字符编码，多行用 `&lt;br&gt;`。已有 UserObject 包装保留其元数据和可编辑图元。

已有图先与打开的编辑器版本核对，保护手工调整。一次性生成器只生成初稿；当前源文件发生手工或后续修改后，以当前源图继续编辑。格式化和重新生成的范围与本轮任务相称。

## 读取与恢复

```bash
python3 "$DIAGRAM_SKILL_DIR/scripts/inspect_diagram.py" path/to/diagram.drawio
python3 "$DIAGRAM_SKILL_DIR/scripts/inspect_diagram.py" path/to/diagram.png

python3 "$DIAGRAM_SKILL_DIR/scripts/inspect_diagram.py" \
  path/to/diagram.png --extract path/to/diagram.drawio
```

通用检查器输出页面、节点、分组、连接、标签、坐标和 PNG 嵌入信息，兼容原生与压缩源图。思维导图再用 `inspect_mindmap.py` 恢复层级。根据输出核对唯一 ID、边端点和几何；跳页导航另查源 XML 中 `mxCell` 或包装对象的 `link` 属性，或在原生界面实际打开目标页。工具成功本身仅证明它实际检查的部分。

普通 PNG 缺少可提取源图时，查找相邻 `.drawio`；来源仍待补时以图片为依据重建并说明范围。

## 按需导出 PNG

只有已选择图片交付时执行：

```bash
python3 "$DIAGRAM_SKILL_DIR/scripts/export_png.py" \
  path/to/diagram.drawio path/to/diagram.png
```

默认浅色、24 像素边距、2 倍缩放、嵌入源图；`--width 1600` 固定宽度，`--transparent` 透明背景，`--theme` 选择主题，`--page` 接受从 1 开始的页号。多页按需分别导出。脚本先在输出目录写临时文件，验证签名、像素和嵌入信息，再原子替换目标文件。

`drawio_cli.py` 先找 `drawio` 命令，再查 macOS 标准应用路径。缺少应用时报告具体依赖；需要安装时按当前环境与用户授权使用官方来源，例如 macOS 的 `brew install --cask drawio`。

PNG 与源文件同目录，文档使用相对链接。图片交付前核对签名、尺寸、嵌入源图和同步情况；纯脑图文件使用 `validate_mindmap.py`。流程图或混合多页文件通过提取结果与源图对照验证同步，各页另外核对各自结构。

## 显示检查与修正

源文件交付在原生 draw.io 中查看，图片交付实际查看 PNG。先用整页检查路径，再按原尺寸或目标阅读比例查看文字与连线：

- 页面标题、起点、分组和主要结果容易定位。
- 主线、分支与回路连续可追踪，条件标签能对应到自己的箭头。
- 文字完整放在节点内，备注和来源位于可读位置，框与线之间留有空间。
- 脑图从根到叶层级清楚，左右重量与分支顺序符合内容。
- 颜色、字体和草图笔触一致，缩放到实际用途仍能读到关键内容。

路径拥挤时先整理内容层级，再调整间距、拐点或分区。文字遮线时调整标签偏移与说明位置；裁切或空白时核对页号、隐藏图层和画布边界。修正后重新查看受影响页面；选择 PNG 交付时重新导出并核对同步。
