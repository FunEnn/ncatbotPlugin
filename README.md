# QQ机器人项目

一个基于 [NcatBot5](https://github.com/ncatbot/NcatBot) 框架的多功能 QQ 机器人，集成了多个实用插件。

> **框架版本**：ncatbot5 v5.3.4+（多平台适配器架构）

## 📦 插件列表

| 插件 | 说明 | 命令 |
| :--- | :--- | :--- |
| [MenuPlugin](./plugins/menu_plugin/) | 功能菜单 | `/菜单` |
| [JmComicPlugin](./plugins/JmComicPlugin/README.md) | 禁漫本子下载 | `/jm <ID>`、`/jmzip <ID>` |
| [Lolicon](./plugins/Lolicon/README.md) | 二次元图片 | `/loli [数量] [标签]`、`/r18 [数量] [标签]` |
| [BilibiliParser](./plugins/BilibiliParser/README.md) | B站视频解析 | `/bparser_login`、自动解析链接 |


### JmComicPlugin 📚

禁漫本子下载插件，支持 PDF 和 ZIP 格式发送。

- `/jm <本子ID>` — 下载并发送 PDF
- `/jmzip <本子ID>` — 下载并发送 ZIP（失败回退 PDF）
- 已下载的文件会缓存，无需重复下载

[📖 查看详细文档](./plugins/JmComicPlugin/README.md)

### [Lolicon] 🎨
二次元图片插件，调用Lolicon API v2发送随机二次元图片。

- 🖼️ 高质量二次元图片获取
- 💾 本地缓存，减少重复下载
- 🔒 R18 内容仅限私聊
- ⚡ 并发下载与分批发送

[📖 查看详细文档](./plugins/Lolicon/README.md)

### BilibiliParser 📺

B站视频链接解析与下载插件，支持 BV/av 号、短链及小程序卡片。

- 🔗 **多格式解析**：自动识别 BV号、av号、b23.tv 短链。
- 📊 **信息摘要**：展示标题、简介、封面及各项统计数据。
- 🎥 **自动发视频**：群聊中自动下载并发送视频文件（需登录）。
- 🔐 **扫码登录**：支持 `/bparser_login` 获取登录态，持久化加密存储。

[📖 查看详细文档](./plugins/BilibiliParser/README.md)


## 🛠️ 安装与配置

### 环境要求

- Python 3.12+
- ncatbot5（`pip install -r requirements.txt`）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/FunEnn/ncatbotPlugin.git
cd ncatbotPlugin
```

#### 2. 安装依赖

**方法一：使用 uv（推荐）**

```bash
pip install uv
uv venv
uv pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

**方法二：使用 pip**

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

#### 3. 初始化配置

**使用 uv（推荐）**

```bash
uv run ncatbot init
```

**使用 pip**

```bash
ncatbot init
```

按照提示输入机器人 QQ 号和管理员 QQ 号，框架会自动生成 `config.yaml` 配置文件。

#### 4. 启动机器人

**使用 uv（推荐）**

```bash
uv run ncatbot run
```

**使用 pip**

```bash
ncatbot run
```

## 📁 项目结构

```
ncatbotPlugin/
├── config.yaml              # 机器人配置（ncatbot init 自动生成）
├── main.py                  # 启动入口（可选，也可直接用 ncatbot run）
├── plugins/                 # 插件目录
│   ├── menu_plugin/         # 菜单插件
│   │   ├── manifest.toml
│   │   └── plugin.py
│   ├── JmComicPlugin/       # 禁漫下载插件
│   │   ├── manifest.toml
│   │   ├── plugin.py
│   │   └── option.yml
│   ├── Lolicon/             # 二次元图片插件
│   │   ├── manifest.toml
│   │   └── plugin.py
│   └── BilibiliParser/      # B站解析插件
│       ├── manifest.toml
│       ├── plugin.py
│       └── db/              # 加密 Cookie 存储
└── requirements.txt
```

## 📋 命令速查

| 命令 | 说明 | 适用场景 |
| :--- | :--- | :--- |
| `/菜单` | 查看所有功能 | 群聊 / 私聊 |
| `/jm <本子ID>` | 下载并发送 PDF | 群聊 / 私聊 |
| `/jmzip <本子ID>` | 下载并发送 ZIP | 群聊 / 私聊 |
| `/loli [数量] [标签]` | 随机二次元图片 | 群聊 / 私聊 |
| `/r18 [数量] [标签]` | R18 图片 | **仅私聊** |
| `/bparser_login` | B站扫码登录 | 群聊 / 私聊 |


## 📝 注意事项

1. 请确保遵守相关法律法规，合理使用各项功能
2. R18 内容仅在私聊中可用
3. 图片版权归原作者所有，请尊重版权
4. 建议定期清理缓存以节省存储空间

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 🙏 鸣谢

- [NcatBot](https://github.com/ncatbot/NcatBot) — 机器人框架
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) — 禁漫爬虫
- [Lolicon API](https://docs.api.lolicon.app/) — 二次元图片 API