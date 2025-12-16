# JmComicPlugin

## 简介
JmComicPlugin 是一个用于 QQ 机器人（NcatBot 框架）的禁漫本子下载插件，支持通过 `/jm <本子ID>` 命令下载禁漫本子并自动发送 PDF 文件，同时支持通过 `/jmzip <本子ID>` 发送 ZIP 压缩包（失败回退发送 PDF）。

## 主要功能
- 通过 `/jm <本子ID>` 指令下载禁漫本子
- 通过 `/jmzip <本子ID>` 指令下载禁漫本子并发送 ZIP（失败回退发送 PDF）
- 自动合成 PDF（优先使用官方 PDF）
- 已下载的 PDF 会直接发送，无需重复下载

## 安装依赖
在插件目录 `plugins/JmComicPlugin` 下运行：

```bash
pip install -r requirements.txt
```

依赖列表：
- jmcomic
- img2pdf

## 使用方法
1. 启动 QQ 机器人（NcatBot 框架）。
2. 在群聊或私聊中发送：
   ```
   /jm <本子ID>
   ```
   例如：`/jm 114514`
3. 如果你希望发送 ZIP 压缩包，在群聊或私聊中发送：
   ```
   /jmzip <本子ID>
   ```
   例如：`/jmzip 114514`
3. 插件会自动下载本子并发送 PDF 文件。
   - 若 PDF 已存在，则直接发送，无需重复下载。

## 常见问题
- **未找到 PDF 或图片？**
  请检查 `option.yml` 的 `base_dir` 路径与实际下载目录是否一致。
- **下载失败或网络问题？**
  检查网络环境，或尝试更换禁漫源域名。

## 支持
如有问题请提交 issue

## 鸣谢

- 本插件基于 [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) 项目开发
- 感谢 [NcatBot](https://github.com/liyihao1110/NcatBot)

