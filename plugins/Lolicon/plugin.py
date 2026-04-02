"""Lolicon 插件 — 调用 Lolicon API v2 发送随机二次元图片。"""

from ncatbot.plugin import NcatBotPlugin
from ncatbot.core import registrar
from ncatbot.event.qq import GroupMessageEvent, PrivateMessageEvent, MessageEvent
from ncatbot.types import MessageArray, Image
from pathlib import Path
import aiohttp
import json
import asyncio
import hashlib
import time
from typing import List, Dict, Optional


class LoliconPlugin(NcatBotPlugin):
    name = "Lolicon"
    version = "1.0.0"

    async def on_load(self):
        self.cache_dir = Path("plugins/Lolicon/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
        self.logger.info(f"{self.name} 插件已加载")

    def _load_cache_index(self) -> Dict:
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载缓存索引失败: {e}")
        return {}

    def _save_cache_index(self):
        try:
            with open(self.cache_index_file, "w", encoding="utf-8") as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存缓存索引失败: {e}")

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"

    async def _download_image(self, url: str) -> Optional[Path]:
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            return cache_path

        try:
            timeout = aiohttp.ClientTimeout(total=10, connect=3)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        if len(content) > 1000:
                            with open(cache_path, "wb") as f:
                                f.write(content)
                            self.cache_index[url] = {
                                "path": str(cache_path),
                                "timestamp": time.time(),
                                "size": len(content),
                            }
                            self._save_cache_index()
                            return cache_path
        except Exception as e:
            self.logger.error(f"下载图片异常: {url}, 错误: {e}")
        return None

    async def _download_images_concurrent(
        self, urls: List[str]
    ) -> List[Optional[Path]]:
        semaphore = asyncio.Semaphore(5)

        async def download_with_semaphore(url: str) -> Optional[Path]:
            async with semaphore:
                return await self._download_image(url)

        tasks = [download_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _call_lolicon_api(
        self, count: int = 1, r18: int = 0, tags: Optional[List[str]] = None
    ) -> List[Dict]:
        api_url = "https://api.lolicon.app/setu/v2"
        params = {"r18": r18, "num": count, "size": "regular"}
        if not tags:
            tags = ["萝莉"]
        for tag in tags:
            params["tag"] = tag
        try:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("error") == "":
                            return data.get("data", [])[:count]
        except Exception as e:
            self.logger.error(f"调用 API 异常: {e}")
        return []

    @registrar.qq.on_command("/loli", "/萝莉", ignore_case=True)
    async def loli_cmd(self, event: MessageEvent):
        """发送随机二次元图片命令"""
        args = event.raw_message.split()
        count = 1
        tag = "萝莉"
        if len(args) > 1:
            try:
                count = int(args[1])
            except ValueError:
                tag = args[1]
        if len(args) > 2:
            tag = args[2]

        count = max(1, min(10, count))
        images_data = await self._call_lolicon_api(count=count, r18=0, tags=[tag])

        if not images_data:
            await event.reply(text="获取图片失败，请稍后重试")
            return

        await self._send_images(event, images_data)

    @registrar.qq.on_private_command("/r18", ignore_case=True)
    async def r18_cmd(self, event: PrivateMessageEvent):
        """发送 R18 二次元图片命令（仅限私聊）"""
        args = event.raw_message.split()
        count = 1
        tag = ""
        if len(args) > 1:
            try:
                count = int(args[1])
            except ValueError:
                tag = args[1]
        if len(args) > 2:
            tag = args[2]

        count = max(1, min(5, count))
        tags = [tag] if tag else ["萝莉"]
        images_data = await self._call_lolicon_api(count=count, r18=1, tags=tags)

        if not images_data:
            await event.reply(text="获取图片失败，请稍后重试")
            return

        await self._send_images(event, images_data)

    async def _send_images(self, event: MessageEvent, images_data: List[Dict]):
        urls = [
            img.get("urls", {}).get("regular", "")
            for img in images_data
            if img.get("urls", {}).get("regular")
        ]
        if not urls:
            await event.reply(text="没有可用的图片链接")
            return

        await event.reply(text="正在获取图片，请稍候...")
        cache_paths = await self._download_images_concurrent(urls)

        # 使用 MessageArray + Image(file=...) 构造消息
        segments = []
        failed_count = 0
        for path in cache_paths:
            if isinstance(path, Exception):
                self.logger.error(f"下载图片异常: {path}")
                failed_count += 1
                continue
            if path and isinstance(path, Path) and path.exists():
                segments.append(Image(file=str(path.absolute())))
            else:
                failed_count += 1

        if not segments:
            await event.reply(text="所有图片下载失败，请稍后重试")
            return

        # 分批发送，每批最多 5 张
        batch_size = min(5, len(segments))
        total_sent = 0

        for i in range(0, len(segments), batch_size):
            batch = segments[i : i + batch_size]
            try:
                await event.reply(rtf=MessageArray(*batch))
                total_sent += len(batch)
            except Exception as e:
                self.logger.error(f"发送图片失败: {e}")

            if i + batch_size < len(segments):
                await asyncio.sleep(0.2)

        if failed_count > 0:
            await event.reply(text=f"发送完成！成功: {total_sent}张，失败: {failed_count}张")