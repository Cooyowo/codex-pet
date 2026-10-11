# Codex Pet 收藏

为 [Codex](https://github.com/openai/codex) 桌面端制作的自定义动画宠物集合，统一遵循 **v2 图集契约**（8 列 × 11 行，含 9 个标准动作行 + 16 个视线朝向）。

This repository collects custom animated pets for the Codex desktop app. Every pet follows the v2 atlas contract: an 8x11 grid with the nine standard animation rows plus sixteen clockwise look directions.

## 目录结构

```text
pets/<pet-id>/
  pet.json            # 宠物清单（id / displayName / description / spriteVersionNumber / spritesheetPath）
  spritesheet.webp    # 1536x2288 图集，单元格 192x208，背景透明
  preview.png         # 11 行动作总览图，便于在 GitHub 上直接预览
tools/validate_pet.py # 离线校验器
.github/workflows/   # 每次 push / PR 自动校验
```

## 安装

把 `pets/<pet-id>` 目录整体复制到本地 Codex 宠物目录：

- macOS / Linux：`~/.codex/pets/<pet-id>/`
- Windows：`C:\Users\<用户名>\.codex\pets\<pet-id>\`

然后在 Codex 的宠物选择器中选择该宠物；如果列表没有刷新，重启一次应用即可。

## 宠物列表

| 宠物 | id | 说明 |
| --- | --- | --- |
| 睡铃雪影娃娃 | `shuiling-xueying-wawa` | 《洛克王国：世界》雪系精灵，冰蓝长发、翠绿头叶、怀抱睡铃兔玩偶。 |
| 异色·睡铃雪影娃娃 | `shuiling-xueying-wawa-shiny` | 同一造型的异色形态：金橙长发、薰衣草紫头叶、琥珀眼、象牙金裙。 |

## 图集契约（v2）

| 行 | 状态 | 使用列 |
| --- | --- | --- |
| 0 | idle | 0-5，另加第 6 列的 v2 中性/待机帧 |
| 1 | running-right | 0-7 |
| 2 | running-left | 0-7 |
| 3 | waving | 0-3 |
| 4 | jumping | 0-4 |
| 5 | failed | 0-7 |
| 6 | waiting | 0-5 |
| 7 | running | 0-5 |
| 8 | review | 0-5 |
| 9 | 视线 A | 000 / 022.5 / 045 / 067.5 / 090 / 112.5 / 135 / 157.5 |
| 10 | 视线 B | 180 / 202.5 / 225 / 247.5 / 270 / 292.5 / 315 / 337.5 |

`000` 表示朝上看（12 点钟方向），不是正面待机；正前方属于指针死区，会回落到中性帧。v2 图集把 `row 0 / column 6` 保留给这个中性（resting）帧，因此它虽然不在 idle 的 6 帧之内，也必须有内容。

## 本地校验

```bash
pip install Pillow
python tools/validate_pet.py
```

校验器会检查清单字段、图集尺寸、每行帧数、必需单元格非空、未使用单元格全透明，以及透明像素下是否残留 RGB 数据。CI 会跑同一个脚本。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。