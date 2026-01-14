import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import ContextTypes

from database import BotDatabase

from venice_ai import VeniceAI

from config import REQUIRED_CHANNELS, WELCOME_MESSAGE, DEVELOPER_USERNAME, ADMIN_CHAT_ID

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class BotHandlers:

    def __init__(self):

        self.db = BotDatabase()

        self.ai = VeniceAI()

        

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user = update.effective_user

        logger.info(f"New user: {user.id}")

        

        self.db.add_user(user.id, user.username, user.first_name, user.last_name)

        

        if self.db.is_user_verified(user.id):

            await self.send_main_menu(update, context)

            return

        

        await self.send_join_channels_message(update, context)

    

    async def send_join_channels_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        message = "🔐 Access Required\n\nTo use this bot, you need to join our channel:\n\n📢 Required Channel:\n@about_tbeh\n\nPlease join the channel to unlock AI features!"

        

        keyboard = []

        for channel in REQUIRED_CHANNELS:

            keyboard.append([InlineKeyboardButton(f"📢 Join {channel['name']}", url=channel["url"])])

        

        keyboard.append([InlineKeyboardButton("✅ I've Joined", callback_data="check_membership")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        await update.message.reply_text(message, reply_markup=reply_markup)

    

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query

        await query.answer()

        

        if query.data == "check_membership":

            self.db.verify_user(query.from_user.id)

            await query.edit_message_text("✅ Verification Successful!\n\nWelcome to TBEH WORM AI!")

            await self.send_welcome_message(update, context)

        

        elif query.data == "chat_worm":

            await query.edit_message_text("🤖 Chat Mode Activated!\n\nYou can now ask me anything!")

            context.user_data['chat_mode'] = True

    

    async def send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        keyboard = [

            [InlineKeyboardButton("🤖 Chat with WORM", callback_data="chat_worm")],

            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/tbeh_owner")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        await context.bot.send_message(

            chat_id=update.effective_chat.id,

            text=WELCOME_MESSAGE,

            reply_markup=reply_markup

        )

    

    async def send_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        keyboard = [

            [InlineKeyboardButton("🤖 Chat with WORM", callback_data="chat_worm")],

            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/tbeh_owner")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        message = f"🎯 TBEH WORM AI\n\nHello {update.effective_user.first_name}! How can I assist you today?"

        

        await update.message.reply_text(message, reply_markup=reply_markup)

    

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user_id = update.effective_user.id

        

        if not self.db.is_user_verified(user_id):

            await update.message.reply_text("❌ Please use /start to verify first.")

            return

        

        if not context.user_data.get('chat_mode', False):

            await self.send_main_menu(update, context)

            return

        

        await self.handle_ai_chat(update, context)

    

    async def handle_ai_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user_id = update.effective_user.id

        user_message = update.message.text

        

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        

        conversation_history = self.db.get_conversation_history(user_id)

        ai_response = self.ai.get_ai_response(conversation_history, user_message)

        

        self.db.add_conversation(user_id, "user", user_message)

        self.db.add_conversation(user_id, "assistant", ai_response)

        

        await update.message.reply_text(f"🤖 {ai_response}")

    

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user_id = update.effective_user.id

        if not self.db.is_user_verified(user_id):

            await update.message.reply_text("❌ Please use /start first.")

            return

        

        context.user_data['chat_mode'] = False

        await self.send_main_menu(update, context)

    

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user_id = update.effective_user.id

        if not self.db.is_user_verified(user_id):

            await update.message.reply_text("❌ Please use /start first.")

            return

        

        self.db.clear_conversation(user_id)

        await update.message.reply_text("✅ Conversation history cleared!")

    

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        help_text = """

🤖 TBEH WORM AI - Help

Commands:

/start - Start bot

/menu - Main menu

/clear - Clear history

/help - This message

How to use:

1. Use /start

2. Join channel

3. Click "Chat with WORM"

4. Start chatting!

Send error here : @dm_tbeh

"""

        await update.message.reply_text(help_text)