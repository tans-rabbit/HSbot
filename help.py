# help.py

import discord
from discord import app_commands
from discord.ui import View, button
import datetime


# ===== help表示 =====
class HelpView(View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.bot = bot
        self.page = 0

    def get_embed(self):

        if self.page == 0:
            embed = discord.Embed(
                title="📖 コマンド一覧（1/2）",
                description="スラッシュコマンド",
                color=0x3498db
            )

            embed.add_field(
                name="🔹 スラッシュコマンド",
                value=(
                    "`/admin` - 管理者専用コマンド確認(管理者専用)\n"
                    "`/daily` - デイリーボーナス\n"
                    "`/dentaku` - 電卓の使い方\n"
                    "`/embednew` - Embed作成\n"
                    "`/embededit` - Embed編集\n"
                    "`/send` - メッセージ送信\n"
                    "`/edit` - メッセージ編集\n"
                    "`/help` - このヘルプ\n"
                    "`/info` - Bot情報\n"
                    "`/omikuji` - おみくじ\n"
                    "`/ping` - 応答速度"
                ),
                inline=False
            )

        else:
            embed = discord.Embed(
                title="📖 コマンド一覧（2/2）",
                description="プレフィックスコマンド",
                color=0x3498db
            )

            embed.add_field(
                name="🔸 プレフィックス",
                value=(
                    "`!calc <式>` - 計算\n"
                    "例: `!calc 2 + 2 * 3`\n\n"
                    "`!dice <NdM>` - サイコロ\n"
                    "例: `!dice 1d100`, `!dice 2d6`"
                ),
                inline=False
            )

        # ✅ timestamp
        embed.timestamp = datetime.datetime.now(datetime.UTC)

        embed.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.display_avatar.url
        )

        return embed

    @button(label="◀️", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )

    @button(label="▶️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page < 1:
            self.page += 1

        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )


# ===== /help =====
@app_commands.command(name="help", description="コマンド一覧を表示")
async def help_command(interaction: discord.Interaction):

    bot = interaction.client

    view = HelpView(bot)

    await interaction.response.send_message(
        embed=view.get_embed(),
        view=view
    )


# ===== /admin =====
@app_commands.command(name="admin", description="管理者専用コマンド一覧を表示")
async def admin_command(interaction: discord.Interaction):

    # ✅ 管理者チェック
    if not interaction.guild or not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ あなたは管理者ではありません",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🔧 管理者専用コマンド",
        description="以下のコマンドは管理者専用です",
        color=0xe74c3c
    )

    embed.add_field(
        name="管理者専用コマンド一覧",
        value=(
            "`/admin` - 管理者専用コマンド確認\n"
            "`/del` - メッセージ削除（入力パネル）\n"
            "`!delall <message_id>` - 指定メッセージ以降全削除\n"
            "`!delnum <user> <count>` - ユーザー指定削除\n"
            "`!deltime <user> <minutes>` - 時間指定削除\n"
            "`!delfrom <user> <message_id>` - 指定位置から削除"
        ),
        inline=False
    )

    embed.timestamp = datetime.datetime.now(datetime.UTC)

    embed.set_footer(
        text=interaction.client.user.name,
        icon_url=interaction.client.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ===== 登録 =====
async def setup(bot):
    bot.tree.add_command(help_command)
    bot.tree.add_command(admin_command)