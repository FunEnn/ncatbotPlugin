"""菜单插件 — 展示 QQ 机器人功能列表。"""

from ncatbot.plugin import NcatBotPlugin
from ncatbot.core import registrar
from ncatbot.event.qq import MessageEvent


class MenuPlugin(NcatBotPlugin):
    name = "menu_plugin"
    version = "1.0.0"

    async def on_load(self):
        self.logger.info(f"{self.name} 插件已加载")

    @registrar.qq.on_command("/菜单", ignore_case=True)
    async def menu_cmd(self, event: MessageEvent):
        menu_text = """🤖 QQ机器人功能菜单 🤖
        
📚 禁漫本子下载 (JmComicPlugin)  
• /jm <本子ID> - 下载禁漫本子并发送PDF
• /jmzip <本子ID> - 下载禁漫本子并发送ZIP(失败回退PDF)

🎨 二次元图片 (Lolicon)
• /loli [数量] [标签] - 发送随机二次元图片
• /r18 [数量] [标签] - 发送R18图片(私聊/权限)
• 示例: /loli 3 萝莉

💡 提示: 直接发送命令即可使用。
"""
        await event.reply(text=menu_text)
