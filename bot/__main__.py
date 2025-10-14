from . import LOGGER, bot_loop
from .core.mltb_client import TgClient
from .core.config_manager import Config
from signal import signal, SIGINT, SIGTERM

Config.load()


async def cleanup():
    """Cleanup function to properly close all connections."""
    LOGGER.info("Shutting down bot gracefully...")

    try:
        # Close Telegram clients
        if TgClient.bot:
            await TgClient.bot.stop()
        if TgClient.user:
            await TgClient.user.stop()

        # Close aria2 and qbittorrent connections
        from .core.torrent_manager import TorrentManager
        if hasattr(TorrentManager, 'aria2') and TorrentManager.aria2:
            await TorrentManager.aria2.close()
        if hasattr(TorrentManager, 'qbittorrent') and TorrentManager.qbittorrent:
            await TorrentManager.qbittorrent.close()

        LOGGER.info("Cleanup completed successfully")
    except Exception as e:
        LOGGER.error(f"Error during cleanup: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    LOGGER.info(f"Received signal {signum}, initiating shutdown...")
    bot_loop.create_task(cleanup())
    bot_loop.stop()


async def main():
    from asyncio import gather
    from .core.startup import (
        load_settings,
        load_configurations,
        save_settings,
        update_aria2_options,
        update_nzb_options,
        update_qb_options,
        update_variables,
    )

    await load_settings()

    await gather(TgClient.start_bot(), TgClient.start_user())
    await gather(load_configurations(), update_variables())

    from .core.torrent_manager import TorrentManager

    await TorrentManager.initiate()
    await gather(
        update_qb_options(),
        update_aria2_options(),
        update_nzb_options(),
    )
    from .helper.ext_utils.files_utils import clean_all
    from .core.jdownloader_booter import jdownloader
    from .helper.ext_utils.telegraph_helper import telegraph
    from .helper.mirror_leech_utils.rclone_utils.serve import rclone_serve_booter
    from .helper.ext_utils.terabox_helper import start_cookie_watcher
    from .modules import (
        initiate_search_tools,
        get_packages_version,
        restart_notification,
    )

    await gather(
        save_settings(),
        jdownloader.boot(),
        clean_all(),
        initiate_search_tools(),
        get_packages_version(),
        restart_notification(),
        telegraph.create_account(),
        rclone_serve_booter(),
        start_cookie_watcher(),
    )


bot_loop.run_until_complete(main())

from .helper.ext_utils.bot_utils import create_help_buttons
from .helper.listeners.aria2_listener import add_aria2_callbacks
from .core.handlers import add_handlers

add_aria2_callbacks()
create_help_buttons()
add_handlers()

# Register signal handlers for graceful shutdown
signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)

LOGGER.info("Bot Started!")

try:
    bot_loop.run_forever()
except KeyboardInterrupt:
    LOGGER.info("Received keyboard interrupt")
finally:
    bot_loop.run_until_complete(cleanup())
    bot_loop.close()
    LOGGER.info("Bot stopped")
