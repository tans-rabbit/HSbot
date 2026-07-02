# db.py

import json
import os
from dotenv import load_dotenv

load_dotenv()

OMIKUJI_CHANNEL_ID = int(os.getenv("OMIKUJI_CHANNEL_ID"))
POINT_CHANNEL_ID = int(os.getenv("POINT_CHANNEL_ID"))
DAILY_CHANNEL_ID = int(os.getenv("DAILY_CHANNEL_ID"))

# ===== 共通読み込み =====
async def load_data(bot, channel_id):

    channel = bot.get_channel(channel_id)

    async for msg in channel.history(limit=10):
        try:
            data = json.loads(msg.content)
            return data, msg
        except:
            continue

    data = {}
    msg = await channel.send(json.dumps(data))
    return data, msg


# ===== おみくじ =====
async def load_omikuji(bot):
    return await load_data(bot, OMIKUJI_CHANNEL_ID)


# ===== ポイント =====
async def load_point(bot):
    return await load_data(bot, POINT_CHANNEL_ID)



async def get_point(bot, user_id):

    data, msg = await load_point(bot)
    uid = str(user_id)

    if uid not in data:
        data[uid] = 1024
        await msg.edit(content=json.dumps(data))

    return data, msg, data[uid]


async def add_point(bot, user_id, amount):

    data, msg = await load_point(bot)
    uid = str(user_id)

    if uid not in data:
        data[uid] = 1024

    data[uid] += amount

    await msg.edit(content=json.dumps(data))

    return data[uid]

# ===== デイリー =====
async def load_daily(bot):
    return await load_data(bot, DAILY_CHANNEL_ID)




# ===== データサイズ取得 =====
async def get_data_size(bot, channel_id):

    data, _ = await load_data(bot, channel_id)

    if data is None:
        return 0, 0  # size, user_count

    # ✅ バイトサイズ
    size = len(json.dumps(data).encode("utf-8"))

    # ✅ ユーザー数
    count = len(data)

    return size, count

#===== データ情報取得 =====

async def get_data_info(bot, channel_id):

    data, _ = await load_data(bot, channel_id)

    if data is None:
        return 0, 0

    size = len(json.dumps(data).encode("utf-8"))
    users = len(data)

    return users, size
