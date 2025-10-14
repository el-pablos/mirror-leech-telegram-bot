"""
Terabox cookie synchronization command.
Allows owner to manually sync cookie from file to database.
"""

from ..helper.ext_utils.bot_utils import new_task
from ..helper.ext_utils.terabox_helper import manual_sync_cookie
from ..helper.telegram_helper.message_utils import send_message


@new_task
async def sync_terabox_cookie(_, message):
    """
    Command handler for /synccookie.
    Manually sync Terabox cookie from file to database.
    """
    # Send processing message
    msg = await send_message(message, "🔄 Syncing Terabox cookie from file to database...")
    
    # Perform sync
    result = await manual_sync_cookie()
    
    # Build response message
    if result['success']:
        if result.get('already_synced'):
            response = (
                "✅ <b>Cookie Already Up-to-Date</b>\n\n"
                f"<b>Message:</b> {result['message']}\n"
                f"<b>Cookie Preview:</b> <code>{result['cookie_preview']}</code>\n"
                f"<b>Hash:</b> <code>{result['hash']}</code>\n\n"
                "ℹ️ The cookie in database is already the same as in file."
            )
        else:
            response = (
                "✅ <b>Cookie Synced Successfully</b>\n\n"
                f"<b>Message:</b> {result['message']}\n"
                f"<b>Cookie Preview:</b> <code>{result['cookie_preview']}</code>\n"
                f"<b>Hash:</b> <code>{result['hash']}</code>\n\n"
                "✅ Cookie has been updated in database.\n"
                "🔄 Bot will now use the new cookie for Terabox downloads."
            )
    else:
        response = (
            "❌ <b>Cookie Sync Failed</b>\n\n"
            f"<b>Error:</b> {result['message']}\n\n"
            "Please check:\n"
            "• File 'terabox.txt' exists in bot root directory\n"
            "• File contains valid cookie string\n"
            "• Database connection is working"
        )
    
    # Update message with result
    await send_message(message, response)

