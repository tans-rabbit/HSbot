import discord
from discord import app_commands
from discord. ext import commands
from discord.ui import View, button
from discord.ui import Modal, TextInput
import random
import datetime
import re
import math
import os
import psutil
import time
import dotenv
import json
import asyncio
from flask import Flask
from threading import Thread

import minigame
import db
import help

print("modules loaded:",discord.__name__,discord.__version__,app_commands.__name__,commands.__name__,View.__name__,Modal.__name__,TextInput.__name__)




RESET = "\033[0m"   # 色リセット
RED = "\033[31m"    # 赤
GREEN = "\033[32m"  # 緑
YELLOW = "\033[33m" # 黄
BLUE = "\033[34m"   # 青
BOLD = "\033[1m"    # 太字

time.sleep(0.1)
print(GREEN,"===== discord.py environment =====",RESET)
time.sleep(0.9)
print(BOLD,"discord.py version:",RESET,discord.__version__)
print(BOLD,"discord.py Intents:",RESET, discord.Intents.default())
print(BOLD,"discord.py Commands:",RESET, commands.Bot)
print(BOLD,"discord.py App Commands:",RESET, app_commands.CommandTree)
print(BOLD,"discord.py UI:",RESET, discord.ui.Modal, discord.ui.TextInput)
print(BOLD,"discord.py Version Info:",RESET, discord.version_info)
print(BOLD,"discord.py Version:",RESET, discord.__version__)
print(BOLD,"discord.py Version Tuple:",RESET, discord.version_info)
print(BOLD,"discord.py Version Release Level:",RESET, discord.version_info.releaselevel)
print(BOLD,"discord.py Version Serial:",RESET, discord.version_info.serial)
print()
time.sleep(0.1)
print(GREEN,"===== system environment =====",RESET)
time.sleep(0.2)
print(BOLD,"file size:",RESET,os.path.getsize(__file__),"bytes")
print(BOLD,"Python Version:",RESET,os.sys.version)
print(GREEN,"=========================================",RESET)
print()
time.sleep(0.2)
print(BLUE,BOLD,"------now setting up the bot...------",RESET,RESET)

# ===== 設定 =====

GUILD_ID = 1234567890  # テストサーバーID（高速反映用・任意）
start_time = datetime.datetime.now()
dotenv.load_dotenv()
time.sleep(0.3)

#===== 環境変数取得 =====

print(BLUE,BOLD,"------loading environment variables...------",RESET,RESET)
TOKEN = os.getenv("TOKEN")  # 環境変数からトークンを取得
OMIKUJI_CHANNEL_ID = int(os.getenv("OMIKUJI_CHANNEL_ID"))  # 環境変数からおみくじチャンネルIDを取得
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # 環境変数からログチャンネルIDを取得

# ===== intents設定 =====

print(BLUE,BOLD,"------setting up intents...------",RESET,RESET)

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

intents.message_content = True   # ←これないと本文読めない
intents.messages = True          # ←GuildMessages

time.sleep(0.1)
print(BLUE,BOLD,"------setting up has been completed------",RESET,RESET)
time.sleep(0.1)

print(YELLOW,"------now starting the bot...------",RESET)
print(YELLOW,BOLD,start_time := datetime.datetime.now(),RESET,RESET)
time.sleep(0.6)

# ===== 管理者専用チェック =====
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# ===== タイムアウト関数 =====
async def timeout_member(member, minutes=5):
    try:
        await member.timeout(datetime.timedelta(minutes=minutes))
    except:
        pass

# ==== ログ送信関数 ===== 

async def send_log(bot, message):

    channel = bot.get_channel(LOG_CHANNEL_ID)

    if channel is None:
        channel = await bot.fetch_channel(LOG_CHANNEL_ID)

    await channel.send(message)




#==== エラー処理 =====

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=discord.Embed(
            title="❌ 権限エラー",
            description="このコマンドを実行する権限がありません。",
            color=0xff0000
        ))

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(
            title="❌ 入力エラー",
            description="引数が不足しています。",
            color=0xff0000
        ))

    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=discord.Embed(
            title="❌ 入力エラー",
            description="引数の形式が正しくありません。",
            color=0xff0000
        ))

    else:
        raise error
    







# === 同期・セットアップ =====

import minigame

loaded = False

@bot.event
async def on_ready():
    print(BLUE,"successfully logged in as",BOLD,f"{bot.user}",RESET)
    global loaded
    if not loaded:
        await minigame.setup(bot)
        await help.setup(bot)
        loaded = True

    await send_log(bot, f"✅ Bot起動：{bot.user} started at {start_time} (uptime: {datetime.datetime.now() - start_time})")
    print("✅ successfully loaded",YELLOW,BOLD,"minigame.py","help.py",RESET,RESET,"commands!")

    try:
        synced = await bot.tree.sync()
        
        print(f"synced:",YELLOW,BOLD,f"{len(synced)}",RESET,"commands have been synced!")
        print(GREEN,[cmd.name for cmd in synced],RESET)
    except Exception as e:
        print(e)
        
    await bot.change_presence(activity=discord.Game(name="/help for commands"))
    

# ===== Flaskサーバー起動（Replit用） =====

app = Flask("")

@app.route("/")
def home():
    return "OK"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()




#=== ステータス変更コマンド =====


@bot.command(name="sm")
async def sm(ctx, *, text):

    # ✅ LOGチャンネル限定
    if ctx.channel.id != LOG_CHANNEL_ID:
        return

    # ✅ ステータス変更
    await bot.change_presence(
        activity=discord.Game(name=text)
    )

    # ✅ 実行者情報
    user = ctx.author

    # ✅ ログ送信
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="🔧 ステータス変更",
        description=(
            f"👤 実行者: {user.mention}\n"
            f"📝 内容: `{text}`"
        ),
        color=0xe67e22
    )

    import datetime as dt
    embed.timestamp = dt.datetime.now(dt.UTC)

    await channel.send(embed=embed)














    

   






# ===== embed作成コマンド =====

@bot.tree.command(name="embednew", description="Embedパネルを作成します")
@app_commands.describe(
    title="タイトル",
    description="説明文",
    color="色（16進数例: 0x00ff00）"
)
async def embednew(interaction: discord.Interaction, title: str, description: str, color: str = "0x2f3136"):

    description = description.replace("\\n", "\n")

    try:
        embed_color = int(color, 16)
    except:
        embed_color = 0x2f3136

    embed = discord.Embed(
        title=title,
        description=description,
        color=embed_color
    )

    

    # ✅ 実行ログを隠す
    
    await interaction.response.send_message("✅ 作成しました", ephemeral=True)

    # ✅ 実際のEmbedはチャンネルに送信
    await interaction.channel.send(embed=embed)
    print(YELLOW,BOLD,f"[{datetime.datetime.now()}]",interaction.user,RESET,"runned /embednew and created embed")

# ===== embed編集コマンド=====

@bot.tree.command(name="embededit", description="既存のEmbedを編集します")
@app_commands.describe(
    message_id="編集するメッセージID",
    title="新しいタイトル",
    description="新しい説明文",
    color="色（例: 0xff0000）"
)
async def embededit(
    interaction: discord.Interaction,
    message_id: str,
    title: str = None,
    description: str = None,
    color: str = None
):
    await interaction.response.defer(ephemeral=True)

    try:
        # メッセージ取得
        message = await interaction.channel.fetch_message(int(message_id))
    except Exception:
        return await interaction.followup.send("❌ メッセージが見つかりません")

    if not message.embeds:
        return await interaction.followup.send("❌ Embedが存在しません")

    old_embed = message.embeds[0]

    # 色処理
    if color:
        try:
            embed_color = int(color, 16)
        except:
            embed_color = old_embed.color
    else:
        embed_color = old_embed.color

    # 新しいEmbed作成（差分更新）
    new_embed = discord.Embed(
        title=title if title else old_embed.title,
        description=description if description else old_embed.description,
        color=embed_color
    )

    
    # フッター保持
    if old_embed.footer:
        new_embed.set_footer(text=old_embed.footer.text)

    # メッセージ編集
    try:
        await message.edit(embed=new_embed)
        await interaction.followup.send("✅ Embedを更新しました")
        print(YELLOW,BOLD,f"[{datetime.datetime.now()}]",interaction.user,RESET,"runned /embededit and edited embed")
    except Exception:
        await interaction.followup.send("❌ 編集に失敗しました（権限不足など）")

# ==== メッセージ送信コマンド =====

@bot.tree.command(name="send", description="メッセージ送信")
async def send(interaction: discord.Interaction, content: str):

    # ✅ 改行対応
    content = content.replace("\\n", "\n")

    # ✅ チャンネルに送信
    await interaction.channel.send(content)

    # ✅ ログ（本人だけ）
    await interaction.response.send_message(
        "✅ 送信しました",
        ephemeral=True
    )
    print(YELLOW,BOLD,f"[{datetime.datetime.now()}]",interaction.user,RESET,"runned /send and sent message")

# === メッセージ編集コマンド =====

@bot.tree.command(name="edit", description="メッセージ編集")
async def edit(interaction: discord.Interaction, message_id: str, content: str):

    content = content.replace("\\n", "\n")

    try:
        message = await interaction.channel.fetch_message(int(message_id))
        await message.edit(content=content)

        await interaction.response.send_message(
            "✅ 編集しました",
            ephemeral=True
        )
        print(YELLOW,BOLD,f"[{datetime.datetime.now()}]",interaction.user,RESET,"runned /edit and edited message")

    except:
        await interaction.response.send_message(
            "❌ メッセージが見つかりません",
            ephemeral=True
        )




# ==== おみくじコマンド =====







#==== pingコマンド =====

@bot.tree.command(name="ping", description="Botの応答速度を確認します")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"応答速度: **{latency}ms**",
        color=0x00ffcc
    )

    embed.timestamp = datetime.datetime.now(datetime.UTC)

    embed.set_footer(
        text=bot.user.name
    )

    print(BOLD,f"{interaction.user}",RESET,"runned /ping")
    print("Latency:",YELLOW,f"{latency}ms",RESET)

    await interaction.response.send_message(embed=embed)







# === ダイスコマンド =====

@bot.command(name="dice")
async def dice(ctx, arg: str):
    pattern = r"(\d+)d(\d+)"
    match = re.fullmatch(pattern, arg)

    if not match:
        embed = discord.Embed(
            title="❌ エラー",
            description="形式が正しくありません\n例: `1d100`, `2d6`",
            color=0xff0000
        )
        return await ctx.send(embed=embed)

    rolls = int(match.group(1))
    sides = int(match.group(2))

    if rolls <= 0 or sides <= 0 or rolls > 200:
        embed = discord.Embed(
            title="❌ エラー",
            description="無効な数値です（回数は1〜200まで）",
            color=0xff0000
        )
        return await ctx.send(embed=embed)

    results = [random.randint(1, sides) for _ in range(rolls)]
    total = sum(results)


    # ===== Embed作成 =====
    if rolls == 1:
        description = f"🎲 **{arg}**\n結果: **{results[0]}**"
    else:
        description = (
            f"🎲 **{arg}**\n"
            f"出目: {results}\n"
            f"合計: **{total}**"
        )

    embed = discord.Embed(
        title="🎲 ダイス結果",
        description=description,
        color=0x3498db
    )
    embed.timestamp = datetime.datetime.now(datetime.UTC)

    embed.set_footer(
        text=bot.user.name
    )
    print(BOLD,f"{ctx.author}",RESET,"runned !dice with argument:",YELLOW,f"{arg}",RESET)

    await ctx.send(embed=embed)







#==== メッセージ削除コマンド =====

@bot.command(name="delall")
@is_admin()
async def delall(ctx, message_id: int):

    try:
        target_message = await ctx.channel.fetch_message(message_id)
    except:
        return await ctx.send("❌ メッセージが見つかりません")

    deleted = 0

    async for msg in ctx.channel.history(limit=None, after=target_message):
        try:
            await msg.delete()
            deleted += 1
        except:
            pass

    embed = discord.Embed(
        title="🧹 チャンネル削除",
        description=f"delall:**{deleted}件** のメッセージを削除しました",
        color=0xff0000
    )
    embed.timestamp = datetime.datetime.now(datetime.UTC)

    embed.set_footer(
        text=ctx.author
    )
    print(RED,BOLD,f"[{datetime.datetime.now()}] {ctx.author}",RESET,f" deleted {deleted} messages after message ID {message_id} using !delall.",RESET)

    await ctx.send(embed=embed)

#=== メッセージ削除コマンド（ユーザー件数指定） =====

@bot.command(name="delnum")
@is_admin()
async def delnum(ctx, member: discord.Member, count: int):

    if count <= 0:
        return await ctx.send("❌ 件数は1以上")

    deleted = 0

    async for msg in ctx.channel.history(limit=1000):
        if msg.author == member:
            try:
                await msg.delete()
                deleted += 1
            except:
                pass

            if deleted >= count:
                break

    await timeout_member(member, 5)

    embed = discord.Embed(
        title="🧹 メッセージ削除",
        description=f"delnum: {member.mention} のメッセージを **{deleted}件** 削除しました。\nタイムアウト：5分",
        color=0xff0000
    )
    embed.timestamp = datetime.datetime.now(datetime.UTC)
    embed.set_footer(text=ctx.author)
    print(RED,BOLD,f"[{datetime.datetime.now()}] {ctx.author}",RESET,f" deleted {deleted} messages from {member} using !delnum, count {count}.",RESET)

    await ctx.send(embed=embed)

#=== メッセージ削除コマンド（ユーザー時間指定） =====

@bot.command(name="deltime")
@is_admin()
async def deltime(ctx, member: discord.Member, minutes: int):

    if minutes <= 0:
        return await ctx.send("❌ 時間は1分以上")

    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes=minutes)

    deleted = 0

    async for msg in ctx.channel.history(limit=None):
        if msg.author == member:
            if now - msg.created_at.replace(tzinfo=None) <= delta:
                try:
                    await msg.delete()
                    deleted += 1
                except:
                    pass

    await timeout_member(member, 5)

    embed = discord.Embed(
        title="🧹 メッセージ削除",
        description=f"deltime: {member.mention} のメッセージを **{deleted}件** 削除しました。\nタイムアウト：5分",
        color=0xff0000
    )
    embed.timestamp = datetime.datetime.now(datetime.UTC)
    embed.set_footer(text=ctx.author)
    print(RED,BOLD,f"[{datetime.datetime.now()}] {ctx.author}",RESET,f" deleted {deleted} messages from {member} using !deltime, within {minutes} minutes.",RESET)

    await ctx.send(embed=embed)

#=== メッセージ削除コマンド（ユーザー指定・メッセージID以降） =====

@bot.command(name="delfrom")
@is_admin()
async def delfrom(ctx, member: discord.Member, message_id: int):

    try:
        target_message = await ctx.channel.fetch_message(message_id)
    except:
        return await ctx.send("❌ メッセージが見つかりません")

    deleted = 0

    async for msg in ctx.channel.history(limit=None, after=target_message):
        if msg.author == member:
            try:
                await msg.delete()
                deleted += 1
            except:
                pass

    await timeout_member(member, 5)

    embed = discord.Embed(
        title="🧹 メッセージ削除",
        description=f"delfrom: {member.mention} のメッセージを **{deleted}件** 削除しました。\nタイムアウト：5分",
        color=0xff0000
    )
    embed.timestamp = datetime.datetime.now(datetime.UTC)
    embed.set_footer(text=ctx.author)
    print(RED,BOLD,f"[{datetime.datetime.now()}] {ctx.author}",RESET,f" deleted {deleted} messages from {member} using !delfrom, after message ID {message_id}.",RESET)

    await ctx.send(embed=embed)

#==== モーダル入力によるメッセージ削除 =====

class DelModal(discord.ui.Modal):

    def __init__(self, mode, member):
        self.mode = mode
        self.member = member

        super().__init__(title="削除設定入力")

        # ===== モードごとに入力欄変更 =====
        if mode == "time":
            self.value = TextInput(
                label="削除する時間（分）",
                placeholder="例: 10",
                required=True
            )

        elif mode == "count":
            self.value = TextInput(
                label="削除する件数",
                placeholder="例: 5",
                required=True
            )

        elif mode == "from":
            self.value = TextInput(
                label="開始メッセージID",
                placeholder="例: 123456789012345678",
                required=True
            )

        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):

        # 管理者チェック
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ 権限がありません", ephemeral=True
            )

        value = self.value.value
        deleted = 0

        try:
            # =====================
            # 時間指定
            # =====================
            if self.mode == "time":
                minutes = int(value)

                now = datetime.datetime.now()
                delta = datetime.timedelta(minutes=minutes)

                async for msg in interaction.channel.history(limit=None):
                    if msg.author == self.member:
                        if now - msg.created_at.replace(tzinfo=None) <= delta:
                            try:
                                await msg.delete()
                                deleted += 1
                            except:
                                pass

            # =====================
            # 件数指定
            # =====================
            elif self.mode == "count":
                count = int(value)

                async for msg in interaction.channel.history(limit=1000):
                    if msg.author == self.member:
                        try:
                            await msg.delete()
                            deleted += 1
                        except:
                            pass

                        if deleted >= count:
                            break

            # =====================
            # 開始地点指定
            # =====================
            elif self.mode == "from":
                target = await interaction.channel.fetch_message(int(value))

                async for msg in interaction.channel.history(limit=None, after=target):
                    if msg.author == self.member:
                        try:
                            await msg.delete()
                            deleted += 1
                        except:
                            pass

        except:
            return await interaction.response.send_message(
                "❌ 入力が不正です",
                ephemeral=True
            )

        # ✅ タイムアウト（※delall以外仕様）
        await timeout_member(self.member, 5)

        # ✅ ログ
        embed = discord.Embed(
            title="🧹 メッセージ削除",
            description=f"{self.member.mention} のメッセージを **{deleted}件** 削除しました。\nタイムアウト：5分",
            color=0xff0000
        )
        embed.timestamp = datetime.datetime.now(datetime.UTC)
        embed.set_footer(text=bot.user.name)
        print(RED,BOLD,f"[{datetime.datetime.now()}] {interaction.user}",RESET,f" deleted {deleted} messages from {self.member} using /del, mode '{self.mode}'.",RESET)

        await interaction.response.send_message(embed=embed)
#==== 上記を踏まえたスラッシュコマンドによるメッセージ削除 =====
@bot.tree.command(name="del", description="メッセージ削除（入力パネル）")
@app_commands.describe(
    mode="削除方法",
    member="対象ユーザー"
)
@app_commands.choices(mode=[
    app_commands.Choice(name="時間指定で削除", value="time"),
    app_commands.Choice(name="件数指定で削除", value="count"),
    app_commands.Choice(name="開始地点から削除", value="from")
])
async def del_command(
    interaction: discord.Interaction,
    mode: app_commands.Choice[str],
    member: discord.Member
):

    # 管理者チェック
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ 権限がありません",
            ephemeral=True
        )

    # ✅ モーダル表示
    await interaction.response.send_modal(DelModal(mode.value, member))







# ==== 計算コマンド =====

import asyncio

@bot.command(name="calc")
async def calc(ctx, *, expr):

    # ✅ 変換
    calc_expr = expr.replace("x", "*").replace("×", "*")
    calc_expr = calc_expr.replace("^", "**")

    display_expr = expr.replace("*", "x").replace("**", "^")

    import math

    allowed = {
        "__builtins__": None,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
        "pi": math.pi,
        "e": math.e
    }

    try:
        # ✅ 1秒でタイムアウト
        result = await asyncio.wait_for(
            asyncio.to_thread(eval, calc_expr, allowed),
            timeout=1.0
        )

        embed = discord.Embed(
            title="🧮 計算結果",
            description=f"**{display_expr}** = `{result}`",
            color=0x2ecc71
        )

        import datetime as dt
        embed.timestamp = dt.datetime.now(dt.UTC)

        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            title="❌ エラー",
            description="計算に時間がかかりすぎています（1秒制限）",
            color=0xff0000
        ))

    except Exception:
        await ctx.send(embed=discord.Embed(
            title="❌ エラー",
            description="計算エラー",
            color=0xff0000
        ))



# === 計算コマンドの使い方 =====

@bot.tree.command(name="dentaku", description="電卓コマンドの使い方を表示")
async def dentaku(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🧮 電卓コマンドの使い方 (!calc)",
        description="`!calc` コマンドで計算ができます",
        color=0x3498db
    )

    embed.add_field(
        name="✅ 基本の使い方",
        value=(
            "`!calc 式`\n"
            "例：\n"
            "`!calc 1+1`\n"
            "`!calc 10*5`\n"
            "`!calc 10/3`"
        ),
        inline=False
    )

    embed.add_field(
        name="✅ 使用できる演算子",
        value=(
            "`+` 足し算\n"
            "`-` 引き算\n"
            "`*,×,x` 掛け算\n"
            "`/` 割り算\n"
            "`**,^` 累乗\n"
        ),
        inline=False
    )

    embed.add_field(
        name="✅ 数学関数",
        value=(
            "`sqrt(16)` → ルート\n"
            "`pow(2,3)` → 累乗\n"
            "`abs(-5)` → 絶対値\n"
            "`round(3.14)` → 四捨五入\n"
            "`max(1,5)` → 最大値\n"
            "`min(1,5)` → 最小値"
        ),
        inline=False
    )

    embed.add_field(
        name="✅ 定数",
        value=(
            "`pi` → 円周率\n"
            "`e` → ネイピア数"
        ),
        inline=False
    )

    embed.add_field(
        name="⚠️ 注意",
        value=(
            "複雑すぎる式はエラーになることがあります"
        ),
        inline=False
    )

    embed.set_footer(text="例: !calc sqrt(16)+2*5")

    await interaction.response.send_message(embed=embed)









# ===== Bot起動 =====

keep_alive()  # Replit用サーバー起動
bot.run(TOKEN)