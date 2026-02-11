from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import admin_filter
from ncatbot.plugin_system import param
from ncatbot.core.event import BaseMessageEvent, PrivateMessageEvent
from ncatbot.core import MessageChain, Image
from ncatbot.utils import get_log
from pathlib import Path
import aiohttp
import json
import asyncio
import hashlib
import time
from typing import List, Dict, Optional

log = get_log("Lolicon")

class Lolicon(NcatBotPlugin):
    name = "Lolicon"
    version = "1.0.0"
    author = "FunEnn"
    description = "调用 Lolicon API v2 发送随机二次元图片"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = Path("plugins/Lolicon/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict:
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"加载缓存索引失败: {e}")
        return {}
    
    def _save_cache_index(self):
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"保存缓存索引失败: {e}")
    
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
                            with open(cache_path, 'wb') as f:
                                f.write(content)
                            
                            self.cache_index[url] = {
                                "path": str(cache_path),
                                "timestamp": time.time(),
                                "size": len(content)
                            }
                            self._save_cache_index()
                            return cache_path
                    else:
                        log.warning(f"下载图片失败: {url}, 状态码: {response.status}")
        except Exception as e:
            log.error(f"下载图片异常: {url}, 错误: {e}")
        
        return None
    
    async def _download_images_concurrent(self, urls: List[str]) -> List[Optional[Path]]:
        async def download_single(url: str) -> Optional[Path]:
            return await self._download_image(url)
        
        semaphore = asyncio.Semaphore(5)
        
        async def download_with_semaphore(url: str) -> Optional[Path]:
            async with semaphore:
                return await download_single(url)
        
        tasks = [download_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _call_lolicon_api(self, count: int = 1, r18: int = 0, tags: List[str] = None) -> List[Dict]:
        api_url = "https://api.lolicon.app/setu/v2"
        params = {
            "r18": r18,
            "num": count,
            "size": "regular"
        }
        
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
                            images_data = data.get("data", [])
                            return images_data[:count]
                        else:
                            log.error(f"API 返回错误: {data.get('error')}")
                    else:
                        log.error(f"API 请求失败: {response.status}")
        except Exception as e:
            log.error(f"调用 API 异常: {e}")
        
        return []
    
    async def on_load(self):
        # 可留空，保持轻量
        log.info(f"{self.name} 插件已加载")
    
    @command_registry.command("loli", aliases=["萝莉"], description="发送随机二次元图片")
    @param(name="count", default=1, help="图片数量 (1-10)")
    @param(name="tag", default="萝莉", help="图片标签")
    async def loli_cmd(self, event: BaseMessageEvent, count: int = 1, tag: str = "萝莉"):
        """发送随机二次元图片命令"""
        max_count = 10
        count = max(1, min(max_count, count))
        
        images_data = await self._call_lolicon_api(count=count, r18=0, tags=[tag])
        
        if not images_data:
            await event.reply("获取图片失败，请稍后重试")
            return
        
        await self.send_images(event, images_data)
    
    @command_registry.command("r18", description="发送 R18 二次元图片（仅限私聊）")
    @param(name="count", default=1, help="图片数量 (1-5)")
    @param(name="tag", default="", help="图片标签")
    async def r18_cmd(self, event: BaseMessageEvent, count: int = 1, tag: str = ""):
        """发送 R18 二次元图片命令（仅限私聊）"""
        # 检查是否为私聊
        if not isinstance(event, PrivateMessageEvent):
            await event.reply("R18 内容仅限私聊使用，群聊中无法发送")
            return
        
        max_count = 5  # R18 内容限制更严格
        count = max(1, min(max_count, count))
        
        tags = [tag] if tag else ["萝莉"]
        images_data = await self._call_lolicon_api(count=count, r18=1, tags=tags)
        
        if not images_data:
            await event.reply("获取图片失败，请稍后重试")
            return
        
        await self.send_images(event, images_data)
    
    @admin_filter
    @command_registry.command("loli_status", aliases=["状态"], description="查看插件状态")
    async def status_cmd(self, event: BaseMessageEvent):
        """查看插件状态（管理员命令）"""
        cache_size = sum(item.get("size", 0) for item in self.cache_index.values())
        cache_count = len(self.cache_index)
        
        status_text = "Lolicon 插件状态:\n"
        status_text += f"缓存图片数量: {cache_count} 张\n"
        status_text += f"缓存大小: {cache_size / 1024 / 1024:.2f} MB\n"
        
        api_status = await self._check_api_status()
        status_text += f"API接口状态: {api_status}"
        
        await event.reply(status_text)
    
    @admin_filter
    @command_registry.command("loli_clear", aliases=["清理缓存"], description="清理图片缓存")
    async def clear_cache_cmd(self, event: BaseMessageEvent):
        """清理图片缓存（管理员命令）"""
        try:
            for cache_path in self.cache_dir.glob("*.jpg"):
                cache_path.unlink()
            
            self.cache_index.clear()
            self._save_cache_index()
            
            await event.reply("缓存清理完成")
        except Exception as e:
            log.error(f"清理缓存失败: {e}")
            await event.reply(f"清理缓存失败: {e}")
    
    async def _check_api_status(self) -> str:
        try:
            api_url = "https://api.lolicon.app/setu/v2"
            params = {"r18": 0, "num": 1, "size": "regular"}
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=10, connect=5)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url, params=params) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("error") == "" and data.get("data"):
                            return f"✅ 正常 (响应时间: {response_time:.2f}s)"
                        else:
                            return f"❌ API返回错误: {data.get('error', '未知错误')}"
                    else:
                        return f"❌ HTTP错误: {response.status}"
        except Exception as e:
            return f"❌ 连接失败: {str(e)}"
    
    async def send_images(self, event: BaseMessageEvent, images_data: List[Dict]):
        urls = []
        
        for image_data in images_data:
            url = image_data.get("urls", {}).get("regular", "")
            if url:
                urls.append(url)
        
        if not urls:
            await event.reply("没有可用的图片链接")
            return
        
        await event.reply("正在获取图片，请稍候...")
        cache_paths = await self._download_images_concurrent(urls)
        
        msg_chains = []
        failed_count = 0
        
        for i, cache_path in enumerate(cache_paths):
            if isinstance(cache_path, Exception):
                log.error(f"下载图片异常: {cache_path}")
                failed_count += 1
                continue
                
            if cache_path and cache_path.exists():
                msg_chains.append(Image(str(cache_path)))
            else:
                failed_count += 1
        
        if not msg_chains:
            await event.reply("所有图片下载失败，请稍后重试")
            return
        
        batch_size = min(5, len(msg_chains))
        total_sent = 0
        
        for i in range(0, len(msg_chains), batch_size):
            batch = msg_chains[i:i + batch_size]
            
            try:
                await event.reply(MessageChain(batch))
                total_sent += len(batch)
            except Exception as e:
                log.error(f"发送图片失败: {e}")
            
            if i + batch_size < len(msg_chains):
                await asyncio.sleep(0.2)
        
        if failed_count > 0:
            await event.reply(f"发送完成！成功: {total_sent}张，失败: {failed_count}张")