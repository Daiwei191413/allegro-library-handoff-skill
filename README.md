# Allegro 封装库交接 Skill

用于 Allegro PCB Editor 的 **symbol / padstack 建库、复核、固定版本交接和目标板采纳验证**。重点是让“库文件检查通过”和“某块 BRD 已安全采用”成为两个可追溯步骤。

本仓库由 `Daiwei191413` 从零编写，适用于新建封装、修改封装、项目间委托交接和量产库复核。

## 交付链

`任务定义 → 接单基线 → 原生库检查 → 固定版本包 → 接收核验 → 隔离板刷新 → 保存重开 → 电气/机械回归 → 人工采纳`

## 完整性工具

工具对明确列出的 `.dra`、`.psm`、`.pad` 及辅助资料生成 SHA-256 清单，再在接收侧复核：

```powershell
python scripts/handoff_package.py snapshot D:/库包 D:/证据/handoff.json symbol.dra symbol.psm pad1.pad
python scripts/handoff_package.py verify D:/库包 D:/证据/handoff.json
python -m unittest discover -s tests -v
```

清单拒绝覆盖已有文件。返回码：`0` 完整性匹配，`1` 文件缺失或变化，`2` 参数/结构/读取错误。匹配不证明尺寸、焊盘、阻焊、钢网或板级连接正确。

## 安装提示

> 请安装这个 Skill：`https://github.com/Daiwei191413/allegro-library-handoff-skill`。先阅读 README.md 和 SKILL.md，运行测试，再按实际 Allegro 版本及库搜索路径执行。

## 调用示例

> 使用 `$allegro-library-handoff-skill` 接收这个 Allegro 封装。保留原库，核对 DRA/PSM/PAD 固定版本，在隔离 BRD 上刷新、保存重开并完成引脚、网络、几何和 DRC 回归；不要把库级通过写成正式量产采纳。

