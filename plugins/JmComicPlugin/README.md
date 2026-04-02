# JmComicPlugin

禁漫本子下载插件，支持通过命令下载本子并自动发送 PDF / ZIP 文件。

> **框架要求**：ncatbot5 v5.3.4+

## ✨ 功能特性

- 📥 通过 `/jm <本子ID>` 下载并发送 PDF
- 📦 通过 `/jmzip <本子ID>` 下载并发送 ZIP（失败自动回退 PDF）
- 💾 已下载的文件自动缓存，无需重复下载
- 📤 支持群聊和私聊发送文件

## 📁 文件结构

```
JmComicPlugin/
├── manifest.toml      # 插件元数据
├── plugin.py           # 插件主逻辑（入口类 JmComicPlugin）
├── option.yml          # jmcomic 下载配置
└── requirements.txt
```

## 📋 命令列表

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `/jm <本子ID>` | 下载并发送 PDF 文件 | `/jm 422866` |
| `/jmzip <本子ID>` | 下载并发送 ZIP（失败回退 PDF） | `/jmzip 422866` |

- 本子 ID 必须是纯数字
- 群聊中通过群文件发送，私聊中通过私聊文件发送

## ⚙️ 配置

下载配置位于 `option.yml`，可调整：

- 下载源域名
- 图片质量
- 下载路径

PDF 输出目录为项目根目录下的 `pdf/` 文件夹。

## ❓ 常见问题

| 问题 | 解决方案 |
| :--- | :--- |
| 未找到 PDF | 检查 `option.yml` 的下载路径配置是否正确 |
| 下载失败 | 检查网络环境，或尝试更换 `option.yml` 中的源域名 |
| 文件发送失败 | 确认机器人在群中有上传文件权限 |

## 🙏 鸣谢

- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) — 禁漫爬虫核心
- [NcatBot](https://github.com/ncatbot/NcatBot) — 机器人框架
