import aiohttp
from io import BytesIO
from PIL import Image as IMG
import base64
from urllib.parse import quote
import time

from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Source
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import At
from graia.application.message.elements.internal import Image
from graia.application.event.messages import Group, Member, GroupMessage
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.application.exceptions import AccountMuted

from sagiri_core.core import SagiriGraiaPlatformCore
from utils import messagechain_to_img


# 插件信息
__name__ = "TraceMoeImageSearcher"
__description__ = "TraceMoe以图搜番"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送搜番后发送图片即可"


platform = SagiriGraiaPlatformCore.get_platform_instance()
loop = platform.get_loop()
bcc = platform.get_bcc()
inc = InterruptControl(bcc)
app: GraiaMiraiApplication = platform.get_app()


@bcc.receiver(GroupMessage, dispatchers=[Kanata([FullMatch('搜番')])])
async def tracemoe_image_searcher(app: GraiaMiraiApplication, member: Member, group: Group):

    image_get: bool = False
    message_received = None

    try:
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id), Plain("请在30秒内发送要搜索的图片呐~")
        ]))
    except AccountMuted:
        return None

    @Waiter.create_using_function([GroupMessage])
    def waiter(
            event: GroupMessage, waiter_group: Group,
            waiter_member: Member, waiter_message: MessageChain
    ):
        nonlocal image_get
        nonlocal message_received
        if time.time() - start_time < 30:
            if all([
                waiter_group.id == group.id,
                waiter_member.id == member.id,
                len(waiter_message[Image]) == len(waiter_message.__root__) - 1
            ]):
                image_get = True
                message_received = waiter_message
                return event
        else:
            print("等待用户发送图片超时！")
            return event

    start_time = time.time()
    await inc.wait(waiter)
    if image_get:
        try:
            await app.sendGroupMessage(
                group,
                await search_bangumi(message_received[Image][0]),
                quote=message_received[Source][0]
            )
        except AccountMuted:
            pass


async def sec_to_str(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


async def search_bangumi(img: Image) -> MessageChain:

    img_url = img.url

    async with aiohttp.ClientSession() as session:
        async with session.get(url=img_url) as resp:
            img_content = await resp.read()

    url = "https://trace.moe/search"
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    image_b64 = base64.b64encode(img_content)

    params = f"data={quote(f'data:image/jpeg;base64,{image_b64.decode()}')}&filter={''}&trial={'0'}"

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=params) as resp:
            result = await resp.json()

    docs = result["docs"]
    if docs:
        try:
            print(docs[0])
            title_chinese = docs[0]["title_chinese"]
            title_origin = docs[0]["title_chinese"]
            file_name = docs[0]["file"]
            anilist_id = docs[0]["anilist_id"]
            time_from = docs[0]["from"]
            time_to = docs[0]["to"]

            t = docs[0]["t"]
            tokenthumb = docs[0]["tokenthumb"]
            thumbnail_url = f"https://trace.moe/thumbnail.php?anilist_id={anilist_id}&file={quote(file_name)}&t={t}&token={tokenthumb}"
            print(thumbnail_url)
            # 下载缩略图
            path = "./plugins/TraceMoeImageSearcher/tempSearchBangumi.jpg"
            async with aiohttp.ClientSession() as session:
                async with session.get(url=thumbnail_url) as resp:
                    thumbnail_content = await resp.read()
            image = IMG.open(BytesIO(thumbnail_content))
            image.save(path)

            url = f"https://trace.moe/info?anilist_id={anilist_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as resp:
                    result = await resp.json()

            result = result[0]
            start_date = f"{result['startDate']['year']}-{result['startDate']['month']}-{result['startDate']['day']}"
            end_date = f"{result['endDate']['year']}-{result['endDate']['month']}-{result['endDate']['day']}"
            score = result["averageScore"]
            message = MessageChain.create([
                    Plain(text="搜索到结果：\n"),
                    Image.fromLocalFile(path),
                    Plain(text=f"name: {title_origin}\n"),
                    Plain(text=f"Chinese name: {title_chinese}\n"),
                    Plain(text=f"file name: {file_name}\n"),
                    Plain(text=f"time: {await sec_to_str(time_from)} ~ {await sec_to_str(time_to)}\n"),
                    Plain(text=f"score: {score}\n"),
                    Plain(text=f"Broadcast date: {start_date} ~ {end_date}\n")
                ])
            return await messagechain_to_img(message=message, max_width=1080, img_fixed=True)
        except Exception as e:
            return MessageChain.create([Plain(text="出错了呢~\n"), Plain(text=str(e))])
    else:
        return MessageChain.create([Plain(text="没有搜索到结果呐~")])
