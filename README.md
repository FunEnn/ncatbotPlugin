# QQ机器人项目

一个基于 [NcatBot](https://github.com/liyihao1110/NcatBot) 框架的多功能QQ机器人，集成了多个实用插件。

## 📦 插件列表

### [JmComicPlugin](./plugins/JmComicPlugin/README.md) 📚
禁漫本子下载插件，支持通过 `/jm <本子ID>` 命令下载禁漫本子并自动发送PDF文件。

**主要功能：**
- 通过 `/jm <本子ID>` 指令下载禁漫本子
- 自动合成PDF（优先使用官方PDF）
- 已下载的PDF会直接发送，无需重复下载

[📖 查看详细文档](./plugins/JmComicPlugin/README.md)

### [Lolicon](./plugins/Lolicon/README.md) 🎨
二次元图片插件，调用Lolicon API v2发送随机二次元图片。

**主要功能：**
- 🖼️ 调用Lolicon API v2获取高质量二次元图片
- 💾 本地缓存功能，减少重复下载
- 🔒 R18内容权限控制，仅限私聊或管理员使用
- 🏷️ 支持标签搜索
- ⚡ 批量发送和转发消息支持

[📖 查看详细文档](./plugins/Lolicon/README.md)

### [BilibiliParser](./plugins/BilibiliParser/README.md) 📺
B站视频解析插件，支持BV/AV号/短链解析。

**主要功能：**
- 解析B站视频
- 支持BV/AV号/短链
- cookie存储至数据库

[📖 查看详细文档](./plugins/BilibiliParser/README.md)

## 🛠️ 安装与配置

### 环境要求
- Python 3.7+
- NcatBot框架

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/FunEnn/ncatbotPlugin.git
cd ncatbotPlugin
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置机器人**
编辑 `main.py` 文件，修改Bot的QQ号：
```python
bot.run(bt_uin="你的机器人QQ号", root="你的QQ号")
```

4. **启动机器人**
```bash
python main.py
```

## 📋 使用命令

### 基础命令
- `/菜单` - 查看所有功能菜单

### JmComicPlugin命令
- `/jm <本子ID>` - 下载禁漫本子并发送PDF
- 示例：`/jm 114514`

### Lolicon命令
- `/loli [数量] [标签]` - 发送随机二次元图片
- `/r18 [数量] [标签]` - 发送R18图片(需权限)
- 示例：`/loli 3 萝莉`、`/loli 白丝`

### BilibiliParser命令
- `/bparser_login` - 登录B站账号(私聊)


## 📝 注意事项

1. 请确保遵守相关法律法规，合理使用各项功能
2. R18内容仅在合适的场合使用
3. 图片版权归原作者所有，请尊重版权
4. 建议定期清理缓存以节省存储空间

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 🙏 鸣谢

- [NcatBot](https://github.com/liyihao1110/NcatBot) - 机器人框架
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) - 禁漫爬虫
- [Lolicon API](https://docs.api.lolicon.app/) - 二次元图片API 