from graia.application.message.elements.internal import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.application.group import Group

from sagiri_core.core import SagiriGraiaPlatformCore

# 插件信息
__name__ = "PluginsManager"
__description__ = "SagiriGraiaPlatform的插件管理器"
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
    for plugin in plugins:
        text += f"\n\n{plugin['name']}:"
        text += f"\n{plugin['description']}"
    await app.sendGroupMessage(group, MessageChain.create([Plain(text=text)]))