"""
Bypass Module
Handle /bypass command to bypass link shorteners
"""

from .. import LOGGER
from ..helper.ext_utils.bot_utils import new_task
from ..helper.ext_utils.link_bypasser import bypass_link, is_shortener_link, get_supported_shorteners
from ..helper.telegram_helper.message_utils import send_message, delete_message
from ..helper.telegram_helper.button_build import ButtonMaker


@new_task
async def bypass_shortlink(_, message):
    """
    Handle /bypass command to bypass link shorteners.
    
    Usage:
        /bypass <shortlink_url>
        /bypass list - Show supported shorteners
    
    Args:
        _: Pyrogram client
        message: Pyrogram message object
    """
    # Parse command
    cmd = message.text.split(maxsplit=1)
    
    # Check if URL is provided
    if len(cmd) == 1:
        help_text = (
            "🔗 <b>Bypass Shortlink Command</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/bypass &lt;shortlink_url&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/bypass https://droplink.co/abc123</code>\n\n"
            "<b>Supported Commands:</b>\n"
            "• <code>/bypass &lt;url&gt;</code> - Bypass a shortlink\n"
            "• <code>/bypass list</code> - Show supported shorteners\n\n"
            "<b>Note:</b> This command supports 50+ shorteners including:\n"
            "Droplink, TNLink, Rocklinks, Linkvertise, OUO.io, and many more!"
        )
        await send_message(message, help_text)
        return
    
    url = cmd[1].strip()
    
    # Check if user wants to see supported shorteners list
    if url.lower() == 'list':
        supported_list = await get_supported_shorteners()
        
        # Add button to close message
        buttons = ButtonMaker()
        buttons.data_button("Close", "help close")
        button = buttons.build_menu()
        
        await send_message(message, supported_list, button)
        return
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        await send_message(
            message,
            "❌ <b>Invalid URL!</b>\n\n"
            "Please provide a valid URL starting with http:// or https://\n\n"
            "<b>Example:</b>\n"
            "<code>/bypass https://droplink.co/abc123</code>"
        )
        return
    
    # Check if it's a known shortener
    if not is_shortener_link(url):
        await send_message(
            message,
            "⚠️ <b>Unknown Shortener!</b>\n\n"
            "The provided URL is not a recognized shortener link.\n\n"
            "Use <code>/bypass list</code> to see supported shorteners."
        )
        return
    
    # Send processing message
    status_msg = await send_message(
        message,
        "⏳ <b>Processing...</b>\n\n"
        f"Bypassing: <code>{url}</code>\n\n"
        "Please wait..."
    )
    
    try:
        # Attempt to bypass the link
        result = await bypass_link(url)
        
        if result['success']:
            # Bypass successful
            original_url = result['original_url']
            
            success_text = (
                "✅ <b>Link Bypassed Successfully!</b>\n\n"
                f"<b>Short Link:</b>\n<code>{url}</code>\n\n"
                f"<b>Origin Link:</b>\n<code>{original_url}</code>\n\n"
                "You can now use the origin link for downloading."
            )
            
            # Add copy button
            buttons = ButtonMaker()
            buttons.url_button("🔗 Open Origin Link", original_url)
            button = buttons.build_menu()
            
            await send_message(message, success_text, button)
            
            # Delete processing message
            await delete_message(status_msg)
            
            LOGGER.info(f"Bypass successful for user {message.from_user.id}: {url} -> {original_url}")
            
        else:
            # Bypass failed
            error_msg = result.get('error', 'Unknown error')
            
            fail_text = (
                "❌ <b>Bypass Failed!</b>\n\n"
                f"<b>Short Link:</b>\n<code>{url}</code>\n\n"
                f"<b>Error:</b>\n{error_msg}\n\n"
                "<b>Possible reasons:</b>\n"
                "• The shortener site is down or slow\n"
                "• The link has expired or is invalid\n"
                "• The shortener has updated their protection\n"
                "• Network connection issues\n\n"
                "Please try again later or use a different link."
            )
            
            await send_message(message, fail_text)
            
            # Delete processing message
            await delete_message(status_msg)
            
            LOGGER.warning(f"Bypass failed for user {message.from_user.id}: {url} - {error_msg}")
            
    except Exception as e:
        error_text = (
            "❌ <b>Unexpected Error!</b>\n\n"
            f"An unexpected error occurred while bypassing the link.\n\n"
            f"<b>Error:</b> {str(e)}\n\n"
            "Please try again later or contact the bot administrator."
        )
        
        await send_message(message, error_text)
        
        # Delete processing message
        try:
            await delete_message(status_msg)
        except:
            pass
        
        LOGGER.error(f"Unexpected error in bypass command for user {message.from_user.id}: {e}", exc_info=True)

