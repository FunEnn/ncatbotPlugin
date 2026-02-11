import asyncio

from ncatbot.core.event import BaseMessageEvent
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import param
from ncatbot.utils import get_log, status
from ncatbot.plugin_system import on_group_at
from ncatbot.core.event import GroupMessageEvent

log = get_log("TestPlugin")


class TestPlugin(NcatBotPlugin):
    name = "TestPlugin"
    version = "1.0.0"
    author = "wyz"
    description = "测试bot插件子类"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_load(self):
        # 可留空，保持轻量
        log.info(f"{self.name} 插件已加载")

    @command_registry.command("test", aliases=["测试"], description="测试接口", prefixes=["@on_group_at"])
    @param(name="input_str", default="你好", help="图片标签")
    async def test_cmd(self, event: BaseMessageEvent, input_str: str = ""):
        commands = command_registry.get_all_commands()
        log_contents = []  # 用于收集日志内容
        for value in commands.values():
            log_content = f"commands:{value.__dict__}"
            log_contents.append(log_content)

        # 将所有日志内容拼接为一个字符串
        result = "\n".join(log_contents)
        await  event.reply(result)

    @on_group_at
    async def handle_group_at(self,event: GroupMessageEvent):
        """
        处理群聊中 @ 机器人的事件
        """
        commands = command_registry.get_all_commands()
        log_contents = []  # 用于收集日志内容
        for value in commands.values():
            log_content = f"commands:{value.__dict__}"
            log_contents.append(log_content)

        # 将所有日志内容拼接为一个字符串
        result = "\n".join(log_contents)
        message_id = await  event.reply(result)
        # 等待 5 秒
        await asyncio.sleep(5)
        await status.global_api.delete_msg(message_id)
