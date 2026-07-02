# minigame.py

from discord import app_commands
import discord
import datetime
import random
import json
import db

# =========================
# 🎴 おみくじ
# =========================
@app_commands.command(name="omikuji", description="1日1回のおみくじ")
async def omikuji(interaction: discord.Interaction):

    bot = interaction.client  # ✅ bot取得

    data, msg = await db.load_omikuji(bot)


    uid = str(interaction.user.id)
    JST = datetime.timezone(datetime.timedelta(hours=9))
    today = str(datetime.datetime.now(JST).date())

    # ✅ 1日制限
    if uid in data and data[uid] == today:
        return await interaction.response.send_message("❌ 今日はもう引きました")

    # ✅ 結果
    results = [
        {"name": "大吉", "text": "今日は最高の1日!✨", "color": 0xffd700},
        {"name": "中吉", "text": "いいことが起きそう!😊", "color": 0x00ffcc},
        {"name": "小吉", "text": "小さな幸せが見つかる日 🍀", "color": 0x66ff66},
        {"name": "吉",   "text": "安定した良い日 👍", "color": 0x3498db},
        {"name": "末吉", "text": "後半から運気アップ? 🔼", "color": 0x95a5a6},
        {"name": "凶",   "text": "慎重にいこう ⚠️", "color": 0xe67e22},
        {"name": "大凶", "text": "今日は無理せず… 😢", "color": 0xe74c3c},
    ]

    result = random.choice(results)

    # ✅ 保存
    data[uid] = today
    await msg.edit(content=json.dumps(data))


    embed = discord.Embed(
        title="🎴 おみくじ",
        description=(
            f"{interaction.user.mention} 結果：**{result['name']}**\n\n"
            f"{result['text']}\n\n"
            
        ),
        color=result["color"]
    )

    import datetime as dt
    embed.timestamp = dt.datetime.now(dt.UTC)

    embed.set_footer(
        text=bot.user.name,
        icon_url=bot.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)







# =========================
# 💰デイリー
# =========================

@app_commands.command(name="daily", description="1日1回5000ポイントもらえる")
async def daily(interaction: discord.Interaction):

    bot = interaction.client

    # ✅ DB読み込み
    data, msg = await db.load_data(bot, db.POINT_CHANNEL_ID)

    uid = str(interaction.user.id)
    JST = datetime.timezone(datetime.timedelta(hours=9))
    today = datetime.datetime.now(JST).date()

    # =========================
    # ✅ 初回
    # =========================
    if uid not in data:
        data[uid] = {
            "points": 1024 + 5000,
            "last_daily": str(today)
        }

        await msg.edit(content=json.dumps(data))

        return await interaction.response.send_message(embed=discord.Embed(
            title="💰 デイリー",
            description=(
                f"{interaction.user.mention}\n"
                f"**+5000pt!**\n"
                f"合計: {data[uid]['points']}pt"
            ),
            color=0x2ecc71
        ))

    user = data[uid]

    # ✅ 古いデータ対応（重要）
    if isinstance(user, int):
        user = {
            "points": user,
            "last_daily": "2000-01-01"
        }
        data[uid] = user

    user["points"] = user.get("points", 1024)
    user["last_daily"] = user.get("last_daily", "2000-01-01")

    last_date = datetime.date.fromisoformat(user["last_daily"])

    # =========================
    # ✅ 今日もうやった？
    # =========================
    if last_date == today:
        return await interaction.response.send_message(embed=discord.Embed(
            f"❌ 今日はもう受け取っています\n\n"
            f"💳 現在: {user['points']}pt",
            ephemeral=True,
            color=0xe74c3c
        ))

    # =========================
    # ✅ 報酬付与
    # =========================
    reward = 5000
    user["points"] += reward
    user["last_daily"] = str(today)

    # 保存
    data[uid] = user
    await msg.edit(content=json.dumps(data))

    # =========================
    # ✅ 表示
    # =========================
    embed = discord.Embed(
        title="💰 デイリーボーナス",
        description=(
            f"{interaction.user.mention}\n\n"
            f"**+5000pt!**\n"
            f"💳 合計: {user['points']}pt"
        ),
        color=0x2ecc71
    )

    import datetime as dt
    embed.timestamp = dt.datetime.now(dt.UTC)

    embed.set_footer(
        text=bot.user.name,
        icon_url=bot.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)







# =========================
# 💰 所持ポイント
# =========================


@app_commands.command(name="bal", description="所持ポイントを確認")
async def bal(
    interaction: discord.Interaction,
    user: discord.User | None = None
):

    bot = interaction.client

    # 未指定なら自分
    if user is None:
        user = interaction.user

    data, msg = await db.load_data(bot, db.POINT_CHANNEL_ID)

    uid = str(user.id)

    # データがなければ作成
    if uid not in data:
        data[uid] = {
            "points": 1024,
            "last_daily": None
        }

        await msg.edit(content=json.dumps(data))

    points = data[uid]["points"]

    embed = discord.Embed(
        title="💰 所持ポイント",
        description=(
            f"{user.mention}\n\n"
            f"現在のポイント: **{points}pt**"
        ),
        color=0xf1c40f
    )

    await interaction.response.send_message(embed=embed)




# =========================
# 🔧 setup（登録）
# =========================
async def setup(bot):
    bot.tree.add_command(omikuji)
    bot.tree.add_command(daily)
    bot.tree.add_command(bal)
