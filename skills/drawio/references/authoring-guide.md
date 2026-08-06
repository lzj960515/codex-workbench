# Draw.io 程序员技术草图规范

## 视觉目标

默认图像呈现一张经过认真整理的程序员白板草图：线条自然、箭头明确、结构清楚、留白充足。草图感服务于亲近感和可修改性，信息层级保持专业、稳定和易读。

新图直接使用原生 draw.io XML 绘制。`assets/technical-sketch-template.drawio` 保存已经验证的节点、连线、箭头、标签、字体和手绘填充参数，创建时以它为起点。

## 原生草图参数

draw.io 使用 Rough.js 渲染草图。所有可见业务形状和业务连线使用：

```text
sketch=1;curveFitting=1;jiggle=2;
```

- `sketch=1` 启用原生手绘渲染。
- `curveFitting=1` 保持曲线和拐角自然、可辨。
- `jiggle=2` 提供适度笔触变化，兼顾草图感与准确性。

节点基础样式：

```text
rounded=1;whiteSpace=wrap;html=1;arcSize=14;
sketch=1;curveFitting=1;jiggle=2;
fillColor=#DCEBFF;strokeColor=#243142;strokeWidth=2;
hachureGap=8;fillWeight=1.5;
fontFamily=Chalkboard SE,Comic Sans MS;fontSize=18;fontColor=#243142;
```

`Chalkboard SE` 和 `Comic Sans MS` 在当前 macOS 可离线使用。中文由系统字体回退保证清晰度；手绘边框、斜线填充和连线承担主要草图感。

## 纸张与配色

使用温暖纸张色画布和深蓝黑墨水：

| 角色 | 颜色 | 用法 |
| --- | --- | --- |
| 纸张 | `#FFFDF5` | 页面背景和边标签背景 |
| 墨水 | `#243142` | 文字、边框、主连线和箭头 |
| 蓝色记号 | `#DCEBFF` | 用户、入口、输入信息 |
| 黄色记号 | `#FFF2CC` | 业务动作、处理步骤 |
| 绿色记号 | `#DFF3E4` | 数据、队列、持久化、已确认状态 |
| 红色记号 | `#F9DFDF` | 失败、风险、重试和人工介入 |
| 淡紫记号 | `#E9E1F7` | Agent、自动化和辅助能力 |
| 橙色墨水 | `#D97736` | 解释性便签和重点圈注 |

一张图选择 2-4 种业务颜色并保持语义一致。手绘填充使用 `hachureGap=8;fillWeight=1.5`；大面积分组使用更稀疏的 `hachureGap=12;fillWeight=1` 或透明背景。

## 叙事与布局

先确定一种主要阅读方向：

- 系统请求、数据流和流水线采用从左到右。
- 生命周期、审批流和逐步处理采用从上到下。
- 上下文图把核心系统放在中央，外部参与者分布在外围。
- 分层架构从上到下排列入口、业务、基础设施和数据。

一张图保留一个主故事。每个视觉区域通常容纳 3-7 个节点；更多细节拆成独立页面或细节图。

推荐几何尺度：

| 元素 | 推荐值 |
| --- | --- |
| 普通节点 | 宽 170-230，高 72-110 |
| 节点内部留白 | 16-24 |
| 水平业务节点间距 | 140-220 |
| 垂直业务节点间距 | 110-180 |
| 分组内边距 | 32-48 |
| 主分区间距 | 80-120 |

节点沿 10 像素网格对齐，再通过轻微高低错落保留白板感。主路径保持清楚的基线，辅助节点围绕主路径布局。

## 节点与分组

- 服务和动作使用手绘圆角矩形。
- 数据库与队列使用带手绘样式的圆柱体。
- 判断使用手绘菱形，所有出边带条件标签。
- 外部参与者使用蓝色记号，核心处理使用黄色记号，数据节点使用绿色记号。
- 失败、重试和人工恢复使用红色记号，并保持与主路径相同的墨水描边。
- 解释使用 `shape=note` 便签和橙色墨水。
- 分组使用透明或极淡填充的虚线手绘边界，标题位于左上角，业务节点保持更强对比。

分组边界承载所有权、部署单元、信任边界或业务阶段。连接线指向内部业务节点，让箭头表达真实关系。

## 连线与箭头

主连线基础样式：

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;
sketch=1;curveFitting=1;jiggle=2;
strokeColor=#243142;strokeWidth=2.5;
endArrow=classic;endFill=1;endSize=18;
fontFamily=Chalkboard SE,Comic Sans MS;fontSize=15;fontColor=#243142;
labelBackgroundColor=#FFFDF5;
```

异步或可选关系增加 `dashed=1;dashPattern=8 6;`。失败路径使用红色墨水 `strokeColor=#B94A48`，同时保留实心箭头。

每条业务连接遵循这些几何条件：

1. 水平端点间保留至少 140 像素，垂直端点间保留至少 110 像素。
2. 标签长度与连线长度匹配，标签两侧各保留至少 40 像素可见线段。
3. 标签移到线条上方或侧面，让主线继续可追踪。
4. 箭头使用 `endSize=18`，箭头尖端与目标框描边清楚分离。
5. 短连接采用无标签箭头，关系说明放在相邻便签或节点副标题。
6. 分支和回路使用显式拐点，保持各自独立的进入方向。

水平边标签使用以下几何偏移：

```xml
<mxGeometry x="0" y="-1" relative="1" as="geometry">
  <mxPoint x="0" y="-16" as="offset" />
</mxGeometry>
```

垂直边标签把 `offset.x` 调整到 40-64，使文字位于线条右侧。标签背景保持纸张色，只包裹文字区域。

## 原生 XML 结构

模板使用未压缩 XML：

```xml
<mxfile host="Agent">
  <diagram id="system-context" name="System Context">
    <mxGraphModel grid="1" gridSize="10" guides="1" connect="1" arrows="1" page="1" pageScale="1" pageWidth="1600" pageHeight="900" background="#FFFDF5">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- business nodes and edges -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

所有业务节点和边使用稳定、可读且唯一的 ID。XML 特殊字符使用实体编码；多行标签使用 `&lt;br&gt;`。边的 `source`、`target` 与业务节点 ID 对应。分组内节点的 `parent` 指向分组 ID，坐标相对分组计算。

## Mermaid 迁移

Mermaid 转换承担已有图的拓扑迁移。转换后把原生元素当作结构草稿，完成以下技术草图重构：

1. 运行 `inspect_diagram.py` 确认节点和边数量。
2. 为所有可见图元应用 Rough.js 草图参数。
3. 按业务语义应用纸张、墨水和记号色。
4. 重新设置节点尺寸与间距，让每条连接满足可见线段要求。
5. 把标签移到线外，确认箭头在目标框前完整露出。
6. 导出并实际查看 PNG，再完成最终交付。

转换生成的 `UserObject` 保存 Mermaid 节点元数据，内部 `mxCell` 仍可单独编辑。保留这些包装节点可以继续使用 draw.io 的 Mermaid 更新能力。

## README 与 PPT

README 图片宽度通常控制在 1400-2000 像素，保证草图笔触和中文标签在缩放后仍清楚。PPT 使用 16:9 横向构图，在画布边缘保留空间，节点文字保持 16 号以上。

默认使用纸张色背景，形成稳定的草图画布。PNG 使用 `--embed-diagram`，使图片携带可恢复的源图信息。

## 视觉验收顺序

1. XML 可解析，节点 ID 唯一，边端点存在。
2. `inspect_diagram.py` 返回预期页面、节点和边。
3. `export_png.py` 返回非零尺寸且 `embedded_diagram` 为 `true`。
4. 在原尺寸检查每条连线、拐点、标签和箭头。
5. 在约 50% 缩放下检查 README 阅读效果。
6. 确认主路径一眼可循，手绘样式一致，分组边界保持轻量。
7. 源图与 PNG 同名相邻，文档使用相对路径引用 PNG。
