import os
import jmcomic
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.core import GroupMessage, PrivateMessage

class JmComicPlugin(NcatBotPlugin):
    name = "JmComicPlugin"
    version = "0.0.1"
    author = "FunEnn"
    description = "禁漫本子下载插件，支持通过/jm命令下载本子并发送PDF文件"

    async def on_load(self):
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.base_dir = os.path.join(project_root, 'pdf')
        # jmcomic 配置
        config_path = os.path.join(os.path.dirname(__file__), "option.yml")
        self.jm_option = jmcomic.JmOption.from_file(config_path)

    @command_registry.command("jm", description="下载禁漫本子并发送PDF文件")
    async def jm_download_cmd(self, event: BaseMessageEvent, album_id: str):
        """下载禁漫本子命令"""
        try:
            if not album_id.isdigit():
                await event.reply("本子ID必须是数字，例如: /jm 422866")
                return
            
            pdf_path = os.path.join(self.base_dir, f"{album_id}.pdf")
            
            if not os.path.exists(pdf_path):
                await event.reply(f"开始下载本子 {album_id}，请稍候...")
                self.jm_option.download_album([album_id])
            
            if os.path.exists(pdf_path):
                await self._send_pdf_file(event, pdf_path)
            else:
                await event.reply("未找到 PDF 文件，可能下载失败。")
        except Exception as e:
            await event.reply(f"下载过程中发生错误: {str(e)}")
    
    async def _send_pdf_file(self, event: BaseMessageEvent, pdf_path: str):
        """发送 PDF 文件"""
        try:
            file_name = os.path.basename(pdf_path)
            
            if isinstance(event, PrivateMessage):
                # 私聊消息
                await self.api.send_private_file(
                    user_id=event.user_id, 
                    file=pdf_path, 
                    name=file_name
                )
            elif isinstance(event, GroupMessage):
                # 群聊消息
                await self.api.send_group_file(
                    group_id=event.group_id, 
                    file=pdf_path, 
                    name=file_name
                )
            else:
                await event.reply(f"PDF文件已准备就绪: {file_name}")
                
        except Exception as e:
            await event.reply(f"发送文件失败: {str(e)}")
