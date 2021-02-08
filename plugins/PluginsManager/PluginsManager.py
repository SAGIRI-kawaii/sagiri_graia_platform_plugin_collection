from graia.application.message.elements.internal import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RegexMatch, RequireParam
from graia.application.group import Group

from sagiri_core.core import SagiriGraiaPlatformCore

# 插件信息
__name__ = "PluginsManager"
__description__ = "SagiriGraiaPlatform的插件管理器(目前还没啥功能)"
__author__ = "SAGIRI-kawaii"
__usage__ = ""


platform: SagiriGraiaPlatformCore = SagiriGraiaPlatformCore.get_platform_instance()
loop = platform.get_loop()
bcc = platform.get_bcc()
app: GraiaMiraiApplication = platform.get_app()


@bcc.receiver("GroupMessage", dispatchers=[Kanata([FullMatch('plugins')])])
async def plugins_manager(app: GraiaMiraiApplication, group: Group):
    plugins = platform.get_plugins()
    text = "SagiriGraiaPlatform\n\n目前已加载插件："
    serial_number = 1
    for plugin in plugins:
        text += f"\n\n{serial_number}. {plugin['name']}:"
        text += f"\n{plugin['description']}"
        serial_number += 1
    text += "\n\n你可输入 'pluginHelp 插件序号' 命令来查看插件详情"
    await app.sendGroupMessage(group, MessageChain.create([Plain(text=text)]))


@bcc.receiver("GroupMessage", dispatchers=[Kanata([RegexMatch('pluginHelp ([0-9]*)')])])
async def plugins_manager(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    plugins = platform.get_plugins()
    target = message.asDisplay()[11:]
    if target.isdigit():
        target = int(target)
        if target > len(plugins):
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="非法插件序号！")]))
        else:
            plugin = plugins[target - 1]
            await app.sendGroupMessage(
                group,
                MessageChain.create([
                    Plain(text=f"插件详细信息："),
                    Plain(text=f"\n\n插件名：{plugin['name']}"),
                    Plain(text=f"\n\n插件描述: {plugin['description']}"),
                    Plain(text=f"\n\n插件作者: {plugin['author']}"),
                    Plain(text=f"\n\n使用方法: {plugin['usage']}")
                ])
            )
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(text="非法插件序号！")]))
