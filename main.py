from ncatbot.core import BotClient, GroupMessage, PrivateMessage
from ncatbot.utils import get_log

bot = BotClient()
_log = get_log()

# ========== 菜单功能 ==========
@bot.on_group_message()
async def on_group_message(msg: GroupMessage):
    if msg.raw_message == "/菜单":
        menu_text = """🤖 QQ机器人功能菜单 🤖
        
📚 禁漫本子下载 (JmComicPlugin)  
• /jm <本子ID> - 下载禁漫本子并发送PDF
• /jmzip <本子ID> - 下载禁漫本子并发送ZIP(失败回退PDF)
• 例如: /jm 114514

🎨 二次元图片 (Lolicon)
• /loli [数量] [标签] - 发送随机二次元图片
• /r18 [数量] [标签] - 发送R18图片(需权限)
• 示例: /loli 3 萝莉、/loli 白丝
"""
        
        await msg.reply(text=menu_text)

@bot.on_private_message()
async def on_private_message(msg: PrivateMessage):
    if msg.raw_message == "/菜单":
        menu_text = """🤖 QQ机器人功能菜单 🤖

📚 禁漫本子下载 (JmComicPlugin)  
• /jm <本子ID> - 下载禁漫本子并发送PDF
• /jmzip <本子ID> - 下载禁漫本子并发送ZIP(失败回退PDF)
• 例如: /jm 114514

🎨 二次元图片 (Lolicon)
• /loli [数量] [标签] - 发送随机二次元图片
• /r18 [数量] [标签] - 发送R18图片(私聊可用)
• 示例: /loli 3 萝莉、/loli 白丝

"""
        
        await msg.reply(text=menu_text)

# ========== 启动 BotClient==========
if __name__ == "__main__":
    bot.run(bt_uin="3387371989", root = "3095852337") # 这里写 Bot 的 QQ 号