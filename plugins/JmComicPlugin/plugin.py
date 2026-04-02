"""JmComic 插件 — 下载禁漫本子并发送 PDF/ZIP 文件。"""

import os
import zipfile
from typing import Optional

import jmcomic
from ncatbot.plugin import NcatBotPlugin
from ncatbot.core import registrar
from ncatbot.event.qq import MessageEvent, GroupMessageEvent, PrivateMessageEvent


class JmComicPlugin(NcatBotPlugin):
    name = "JmComicPlugin"
    version = "1.0.0"

    async def on_load(self):
        # 获取项目根目录
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )
        self.base_dir = os.path.join(project_root, "pdf")
        # jmcomic 配置
        config_path = os.path.join(os.path.dirname(__file__), "option.yml")
        self.jm_option = jmcomic.JmOption.from_file(config_path)

        os.makedirs(self.base_dir, exist_ok=True)
        self.logger.info(f"{self.name} 插件已加载")

    async def on_close(self):
        self.logger.info(f"{self.name} 插件已卸载")

    def _pdf_path(self, album_id: str) -> str:
        return os.path.join(self.base_dir, f"{album_id}.pdf")

    def _zip_path(self, album_id: str) -> str:
        return os.path.join(self.base_dir, f"{album_id}.zip")

    async def _ensure_pdf(self, event: MessageEvent, album_id: str) -> Optional[str]:
        pdf_path = self._pdf_path(album_id)

        if os.path.exists(pdf_path):
            return pdf_path

        await event.reply(text=f"开始下载本子 {album_id}，请稍候...")
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

    @registrar.qq.on_command("/jm")
    async def jm_download_cmd(self, event: MessageEvent, album_id: str):
        """下载禁漫本子并发送 PDF 文件"""
        try:
            if not album_id.isdigit():
                await event.reply(text="本子ID必须是数字，例如: /jm 422866")
                return

            pdf_path = await self._ensure_pdf(event, album_id)
            if not pdf_path:
                await event.reply(text="未找到 PDF 文件，可能下载失败。")
                return

            await self._send_file(event, pdf_path)
        except Exception as e:
            await event.reply(text=f"下载过程中发生错误: {str(e)}")

    @registrar.qq.on_command("/jmzip")
    async def jmzip_download_cmd(self, event: MessageEvent, album_id: str):
        """下载禁漫本子并发送 ZIP 压缩包（失败则回退发送 PDF）"""
        try:
            if not album_id.isdigit():
                await event.reply(text="本子ID必须是数字，例如: /jmzip 422866")
                return

            zip_path = self._zip_path(album_id)

            if not os.path.exists(zip_path):
                pdf_path = await self._ensure_pdf(event, album_id)
                if not pdf_path:
                    await event.reply(text="未找到 PDF 文件，可能下载失败。")
                    return

                await event.reply(text=f"开始打包本子 {album_id} ，请稍候...")
                zip_path = self._build_zip_from_pdf(album_id, pdf_path)

            try:
                await self._send_file(event, zip_path)
            except Exception as e:
                await event.reply(text=f"ZIP发送失败，尝试发送PDF... ({str(e)})")
                pdf_path = self._pdf_path(album_id)
                if os.path.exists(pdf_path):
                    await self._send_file(event, pdf_path)
                else:
                    await event.reply(text="PDF 文件不存在，无法回退发送。")
        except Exception as e:
            await event.reply(text=f"jmzip 执行过程中发生错误: {str(e)}")

    async def _send_file(self, event: MessageEvent, file_path: str):
        """发送文件（PDF/ZIP）"""
        file_name = os.path.basename(file_path)

        if isinstance(event, PrivateMessageEvent):
            await self.api.qq.send_private_file(
                user_id=event.user_id,
                file=file_path,
                name=file_name,
            )
        elif isinstance(event, GroupMessageEvent):
            await self.api.qq.send_group_file(
                group_id=event.group_id,
                file=file_path,
                name=file_name,
            )
        else:
            await event.reply(text=f"文件已准备就绪: {file_name}")
