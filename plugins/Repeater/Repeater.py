import threading
import re

from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.event.messages import Group
from graia.application.exceptions import AccountMuted

from sagiri_core.core import SagiriGraiaPlatformCore


# 插件信息
__name__ = "Repeater"
__description__ = "复读🐓（x"
__author__ = "SAGIRI-kawaii"
__usage__ = "两个相同message即可触发复读"


platform = SagiriGraiaPlatformCore.get_platform_instance()
loop = platform.get_loop()
bcc = platform.get_bcc()
app: GraiaMiraiApplication = platform.get_app()

group_repeat = {}
lock = threading.Lock()


@bcc.receiver("GroupMessage")
async def repeater(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    group_id = group.id
    message_serialization = message.asSerializationString()
    message_serialization = message_serialization.replace(
        "[mirai:source:" + re.findall(r'\[mirai:source:(.*?)]', message_serialization, re.S)[0] + "]",
        ""
    )

    lock.acquire()
    if group_id in group_repeat.keys():
        group_repeat[group.id]["lastMsg"] = group_repeat[group.id]["thisMsg"]
        group_repeat[group.id]["thisMsg"] = message_serialization
        if group_repeat[group.id]["lastMsg"] != group_repeat[group.id]["thisMsg"]:
            group_repeat[group.id]["stopMsg"] = ""
        else:
            if group_repeat[group.id]["thisMsg"] != group_repeat[group.id]["stopMsg"]:
                group_repeat[group.id]["stopMsg"] = group_repeat[group.id]["thisMsg"]
                try:
                    await app.sendGroupMessage(group, message.asSendable())
                except AccountMuted:
                    pass
    else:
        group_repeat[group_id] = {"lastMsg": "", "thisMsg": "", "stopMsg": ""}
    lock.release()
