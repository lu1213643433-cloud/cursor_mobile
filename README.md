# 📒 iPhone 记账快捷指令

一个 iPhone 快捷指令，帮助你快速记录日常支出，数据以 CSV 格式存储在本地 iCloud Drive 中，可直接用 Excel / Numbers 打开。

## 特性

- **一键记账**：输入金额 → 选择类别 → 填写备注，3 步完成
- **本地存储**：数据保存为 CSV 文件，存储在 iCloud Drive，无需联网或第三方服务
- **Excel 兼容**：CSV 文件可直接用 Excel、Numbers、WPS 等表格软件打开
- **自动同步**：iCloud Drive 自动同步到所有设备
- **完全离线**：快捷指令本身不联网，保护隐私

## 快速开始

### 1. 安装快捷指令

在 iPhone 上下载 `记账助手.shortcut` 文件，系统会自动打开「快捷指令」App 并提示添加。

### 2. 创建 CSV 文件

将 `记账示例_导入Numbers.csv` 保存到 iPhone 的 `iCloud Drive → Shortcuts` 目录，重命名为 `记账.csv`。

或手动创建只含表头的空文件：

```
日期,金额,类别,备注
```

### 3. 开始记账

打开「快捷指令」App → 点击「记账助手」→ 按提示输入即可。

## 文件说明

| 文件 | 说明 |
|------|------|
| `记账助手.shortcut` | iPhone 快捷指令文件，直接导入使用 |
| `记账示例_导入Numbers.csv` | CSV 模板（含示例数据），可导入 Numbers 或 Excel |
| `generate_shortcut.py` | 生成 `.shortcut` 文件的 Python 脚本 |
| `GUIDE.md` | 详细使用指南 |

## 预设类别

`餐饮` · `交通` · `购物` · `日用` · `娱乐` · `医疗` · `教育` · `其他`

## 自定义

编辑 `generate_shortcut.py` 中的 `CATEGORIES` 列表可修改类别，然后运行：

```bash
python3 generate_shortcut.py
```

重新生成 `.shortcut` 文件并导入 iPhone 即可。

## 详细文档

请参阅 [GUIDE.md](GUIDE.md) 获取完整的安装、使用和自定义说明。
