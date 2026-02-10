import os
import zipfile
import tempfile

import jmcomic
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.core import GroupMessage, PrivateMessage
from ncatbot.core import MessageChain, Image

class JmComicPlugin(NcatBotPlugin):
    name = "JmComicPlugin"
    version = "0.0.1"
    author = "FunEnn"
    description = "禁漫本子下载插件，支持通过/jm命令下载本子并发送PDF文件"

    async def on_load(self):
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.base_dir = os.path.join(project_root, 'pdf')
        # 创建封面临时目录
        self.cover_dir = os.path.join(project_root, 'cover')
        # jmcomic 配置
        config_path = os.path.join(os.path.dirname(__file__), "option.yml")
        self.jm_option = jmcomic.JmOption.from_file(config_path)

        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.cover_dir, exist_ok=True)

    def _pdf_path(self, album_id: str) -> str:
        return os.path.join(self.base_dir, f"{album_id}.pdf")

    def _zip_path(self, album_id: str) -> str:
        return os.path.join(self.base_dir, f"{album_id}.zip")

    async def _ensure_pdf(self, event: BaseMessageEvent, album_id: str) -> str | None:
        pdf_path = self._pdf_path(album_id)

        if os.path.exists(pdf_path):
            return pdf_path

        await event.reply(f"开始下载本子 {album_id}，请稍候...")
        self.jm_option.download_album([album_id])

        if os.path.exists(pdf_path):
            return pdf_path

        return None

    def _build_zip_from_pdf(self, album_id: str, pdf_path: str) -> str:
        zip_path = self._zip_path(album_id)
        pdf_name_in_zip = os.path.basename(pdf_path)

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zf:
            zf.write(pdf_path, arcname=pdf_name_in_zip)

        return zip_path

    @command_registry.command("jm", description="下载禁漫本子并发送PDF文件")
    async def jm_download_cmd(self, event: BaseMessageEvent, album_id: str):
        """下载禁漫本子命令"""
        try:
            if not album_id.isdigit():
                await event.reply("本子ID必须是数字，例如: /jm 422866")
                return

            pdf_path = await self._ensure_pdf(event, album_id)
            if not pdf_path:
                await event.reply("未找到 PDF 文件，可能下载失败。")
                return

            await self._send_file(event, pdf_path)
        except Exception as e:
            await event.reply(f"下载过程中发生错误: {str(e)}")

    @command_registry.command("jmzip", description="下载禁漫本子并发送ZIP压缩包（失败则回退发送PDF）")
    async def jmzip_download_cmd(self, event: BaseMessageEvent, album_id: str):
        """下载禁漫本子并发送 ZIP"""
        try:
            if not album_id.isdigit():
                await event.reply("本子ID必须是数字，例如: /jmzip 422866")
                return

            zip_path = self._zip_path(album_id)

            if not os.path.exists(zip_path):
                pdf_path = await self._ensure_pdf(event, album_id)
                if not pdf_path:
                    await event.reply("未找到 PDF 文件，可能下载失败。")
                    return

                await event.reply("开始打包本子 {album_id} ，请稍候...")
                zip_path = self._build_zip_from_pdf(album_id, pdf_path)

            try:
                await self._send_file(event, zip_path)
            except Exception as e:
                await event.reply(f"ZIP发送失败，尝试发送PDF... ({str(e)})")
                pdf_path = self._pdf_path(album_id)
                if os.path.exists(pdf_path):
                    await self._send_file(event, pdf_path)
                else:
                    await event.reply("PDF 文件不存在，无法回退发送。")
        except Exception as e:
            await event.reply(f"jmzip 执行过程中发生错误: {str(e)}")

    async def _send_file(self, event: BaseMessageEvent, file_path: str):
        """发送文件（PDF/ZIP）"""
        file_name = os.path.basename(file_path)

        if isinstance(event, PrivateMessage):
            await self.api.send_private_file(
                user_id=event.user_id,
                file=file_path,
                name=file_name,
            )
        elif isinstance(event, GroupMessage):
            await self.api.send_group_file(
                group_id=event.group_id,
                file=file_path,
                name=file_name,
            )
        else:
            await event.reply(f"文件已准备就绪: {file_name}")

    @command_registry.command("query", description="根据关键词搜索禁漫本子")
    async def jm_query_cmd(self, event: BaseMessageEvent, search_query: str):
        """搜索禁漫本子命令"""
        try:
            if not search_query:
                await event.reply("请提供搜索关键词，例如: /query MANA 无修正 或 /query 427413")
                return

            # 创建JmClient实例
            client = self.jm_option.new_jm_client()
            
            await event.reply(f"正在搜索关键词: {search_query}，请稍候...")
            
            # 搜索漫画
            page = client.search_site(search_query=search_query, page=1)
            
            if page.total == 0:
                await event.reply(f"未找到与 '{search_query}' 相关的本子")
                return
            
            # 只显示前5个结果（因为要下载封面）
            results = []
            count = 0
            for album_id, title in page:
                if count >= 5:
                    break
                results.append((album_id, title))
                count += 1
            
            # 下载封面并准备消息
            message_chains = []
            
            # 添加总结果信息
            message_chains.append(Image(""))  # 占位符，后面会替换
            message_chains.append(f"搜索结果 (共{page.total}个本子，当前第1页):\n\n")
            
            for album_id, title in results:
                # 下载封面
                cover_path = os.path.join(self.cover_dir, f"{album_id}.jpg")
                try:
                    client.download_album_cover(album_id, cover_path)
                    
                    # 添加封面和信息到消息链
                    message_chains.append(Image(cover_path))
                    message_chains.append(f"[{album_id}]: {title}\n")
                except Exception as e:
                    # 如果下载封面失败，只添加文本信息
                    message_chains.append(f"[{album_id}]: {title} (封面下载失败)\n")
            
            if page.total > 5:
                message_chains.append(f"\n... 还有 {page.total - 5} 个结果未显示")
            
            # 移除第一个占位符
            if message_chains and isinstance(message_chains[0], Image):
                message_chains.pop(0)
            
            # 发送消息
            await event.reply(MessageChain(message_chains))
            
        except Exception as e:
            await event.reply(f"搜索过程中发生错误: {str(e)}")