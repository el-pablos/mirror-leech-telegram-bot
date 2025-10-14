"""
Terabox download helper with cookie-based authentication.
Supports downloading files from Terabox/1024tera using user cookies.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, Optional, Callable
from datetime import datetime
from aiofiles import open as aiopen
from aiofiles.os import path as aiopath
from asyncio import create_task, sleep

from ... import LOGGER, DOWNLOAD_DIR


# Terabox domains that are supported
TERABOX_DOMAINS = [
    "terabox.com",
    "nephobox.com",
    "4funbox.com",
    "mirrobox.com",
    "momerybox.com",
    "teraboxapp.com",
    "1024tera.com",
    "terabox.app",
    "gibibox.com",
    "goaibox.com",
    "terasharelink.com",
    "teraboxlink.com",
    "freeterabox.com",
    "1024terabox.com",
    "teraboxshare.com",
    "terafileshare.com",
    "terabox.club",
]


def is_terabox_link(url: str) -> bool:
    """
    Check if URL is a Terabox link.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if URL is from Terabox, False otherwise
    """
    if not url:
        return False
    
    url_lower = url.lower()
    return any(domain in url_lower for domain in TERABOX_DOMAINS)


async def read_terabox_cookie_from_db() -> Optional[str]:
    """
    Read Terabox cookie from MongoDB database.

    Returns:
        str: Cookie string if exists in database, None otherwise
    """
    try:
        from .db_handler import database
        from ...core.mltb_client import TgClient

        if database.db is None:
            return None

        # Get cookie from database
        cookie_doc = await database.db.settings.cookies.find_one(
            {"_id": TgClient.ID},
            {"terabox_cookie": 1}
        )

        if cookie_doc and "terabox_cookie" in cookie_doc:
            cookie = cookie_doc["terabox_cookie"]
            if cookie and isinstance(cookie, str):
                LOGGER.info("Terabox cookie loaded from database")
                return cookie.strip()

        return None

    except Exception as e:
        LOGGER.error(f"Error reading Terabox cookie from database: {e}")
        return None


async def read_terabox_cookie_from_file() -> Optional[str]:
    """
    Read Terabox cookie from terabox.txt file.
    Ignores comment lines (starting with #) and empty lines.
    Supports both header string format and Netscape cookie format.

    Returns:
        str: Cookie string if file exists and valid, None otherwise
    """
    cookie_file = "terabox.txt"

    try:
        if not await aiopath.exists(cookie_file):
            LOGGER.warning(f"Terabox cookie file not found: {cookie_file}")
            return None

        async with aiopen(cookie_file, 'r') as f:
            content = await f.read()

        # Check if it's Netscape format
        if "# Netscape HTTP Cookie File" in content:
            # Parse Netscape format
            cookie_dict = {}
            for line in content.split('\n'):
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse Netscape cookie line
                # Format: domain flag path secure expiration name value
                parts = line.split('\t')
                if len(parts) >= 7:
                    name = parts[5]
                    value = parts[6]
                    # Only keep ndus and lang cookies
                    if name in ['ndus', 'lang']:
                        cookie_dict[name] = value

            # Build cookie string
            if cookie_dict:
                cookie = '; '.join([f"{k}={v}" for k, v in cookie_dict.items()]) + ';'
                LOGGER.info("Terabox cookie loaded from file (Netscape format)")
                return cookie
        else:
            # Parse header string format
            lines = content.split('\n')
            cookie_lines = []
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    cookie_lines.append(line)

            if not cookie_lines:
                LOGGER.warning("Terabox cookie file is empty or contains only comments")
                return None

            # Join all non-comment lines
            cookie = ' '.join(cookie_lines)

            # Basic validation - check if cookie has required format
            if "ndus=" not in cookie and "lang=" not in cookie:
                LOGGER.warning("Terabox cookie appears invalid (missing ndus or lang)")
                return None

            LOGGER.info("Terabox cookie loaded from file (header format)")
            return cookie

        return None

    except Exception as e:
        LOGGER.error(f"Error reading Terabox cookie from file: {e}")
        return None


async def get_cookie_metadata_from_db() -> Optional[Dict]:
    """
    Get Terabox cookie metadata from database.

    Returns:
        dict: Cookie metadata (hash, updated timestamp, source) or None
    """
    try:
        from .db_handler import database
        from ...core.mltb_client import TgClient

        if database.db is None:
            return None

        cookie_doc = await database.db.settings.cookies.find_one(
            {"_id": TgClient.ID},
            {
                "terabox_cookie_hash": 1,
                "terabox_cookie_updated": 1,
                "terabox_cookie_source": 1
            }
        )

        if cookie_doc:
            return {
                'hash': cookie_doc.get('terabox_cookie_hash'),
                'updated': cookie_doc.get('terabox_cookie_updated'),
                'source': cookie_doc.get('terabox_cookie_source')
            }

        return None

    except Exception as e:
        LOGGER.error(f"Error getting cookie metadata from database: {e}")
        return None


async def sync_cookie_file_to_db() -> bool:
    """
    Sync Terabox cookie from file to database if file is newer or different.

    Returns:
        bool: True if synced successfully, False otherwise
    """
    try:
        # Read cookie from file
        file_cookie = await read_terabox_cookie_from_file()
        if not file_cookie:
            LOGGER.debug("No cookie found in file, skipping sync")
            return False

        # Calculate file cookie hash
        file_hash = hashlib.sha256(file_cookie.encode()).hexdigest()

        # Get database cookie metadata
        db_metadata = await get_cookie_metadata_from_db()

        # Check if sync is needed
        if db_metadata and db_metadata.get('hash') == file_hash:
            LOGGER.debug("Cookie in database is already up-to-date")
            return False

        # Sync to database
        LOGGER.info("Syncing cookie from file to database...")
        success = await save_terabox_cookie_to_db(file_cookie, source='file')

        if success:
            LOGGER.info(f"✅ Cookie synced successfully (hash: {file_hash[:16]}...)")

        return success

    except Exception as e:
        LOGGER.error(f"Error syncing cookie file to database: {e}")
        return False


async def read_terabox_cookie() -> Optional[str]:
    """
    Read Terabox cookie with smart fallback mechanism.
    Priority: File (if newer) > Database > File (if no database)

    Returns:
        str: Cookie string if found, None otherwise
    """
    # Try to sync file to database first (if file is newer)
    await sync_cookie_file_to_db()

    # Try database first
    cookie = await read_terabox_cookie_from_db()
    if cookie:
        return cookie

    # Fallback to file
    cookie = await read_terabox_cookie_from_file()
    if cookie:
        # Save to database for future use
        await save_terabox_cookie_to_db(cookie, source='file')
        return cookie

    return None


async def save_terabox_cookie_to_db(cookie: str, source: str = 'manual') -> bool:
    """
    Save Terabox cookie to MongoDB database with metadata.

    Args:
        cookie: Cookie string to save
        source: Source of cookie ('file', 'manual', 'command')

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        from .db_handler import database
        from ...core.mltb_client import TgClient

        if database.db is None:
            return False

        # Calculate cookie hash for change detection
        cookie_hash = hashlib.sha256(cookie.encode()).hexdigest()

        # Save with metadata
        await database.db.settings.cookies.update_one(
            {"_id": TgClient.ID},
            {
                "$set": {
                    "terabox_cookie": cookie,
                    "terabox_cookie_updated": datetime.utcnow(),
                    "terabox_cookie_hash": cookie_hash,
                    "terabox_cookie_source": source
                }
            },
            upsert=True
        )

        LOGGER.info(f"Terabox cookie saved to database (source: {source}, hash: {cookie_hash[:16]}...)")
        return True

    except Exception as e:
        LOGGER.error(f"Error saving Terabox cookie to database: {e}")
        return False


async def save_youtube_cookie_to_db(cookie: str) -> bool:
    """
    Save YouTube cookie to MongoDB database.

    Args:
        cookie: Cookie string or file content to save

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        from .db_handler import database
        from ...core.mltb_client import TgClient

        if database.db is None:
            return False

        await database.db.settings.cookies.update_one(
            {"_id": TgClient.ID},
            {"$set": {"youtube_cookie": cookie}},
            upsert=True
        )

        LOGGER.info("YouTube cookie saved to database")
        return True

    except Exception as e:
        LOGGER.error(f"Error saving YouTube cookie to database: {e}")
        return False


async def read_youtube_cookie_from_db() -> Optional[str]:
    """
    Read YouTube cookie from MongoDB database.

    Returns:
        str: Cookie string if exists in database, None otherwise
    """
    try:
        from .db_handler import database
        from ...core.mltb_client import TgClient

        if database.db is None:
            return None

        # Get cookie from database
        cookie_doc = await database.db.settings.cookies.find_one(
            {"_id": TgClient.ID},
            {"youtube_cookie": 1}
        )

        if cookie_doc and "youtube_cookie" in cookie_doc:
            cookie = cookie_doc["youtube_cookie"]
            if cookie and isinstance(cookie, str):
                LOGGER.info("YouTube cookie loaded from database")
                return cookie

        return None

    except Exception as e:
        LOGGER.error(f"Error reading YouTube cookie from database: {e}")
        return None


def format_cookie_for_terabox(cookie: str) -> str:
    """
    Format cookie string to ensure compatibility with TeraboxDL library.
    Extracts only essential cookies (ndus, lang) and formats them properly.

    Args:
        cookie: Raw cookie string

    Returns:
        str: Formatted cookie string with only essential cookies
    """
    # Extract ndus and lang values
    cookie_dict = {}

    # Split by semicolon and parse each cookie
    for part in cookie.split(';'):
        part = part.strip()
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            # Only keep essential cookies
            if key in ['ndus', 'lang', 'ndut_fmt', 'browserid', 'csrfToken']:
                cookie_dict[key] = value

    # Build formatted cookie string
    if 'ndus' in cookie_dict and 'lang' in cookie_dict:
        formatted = f"lang={cookie_dict['lang']}; ndus={cookie_dict['ndus']};"
        LOGGER.info(f"Formatted cookie: lang={cookie_dict['lang']}; ndus={cookie_dict['ndus'][:20]}...")
        return formatted
    else:
        LOGGER.warning("Cookie missing essential fields (ndus or lang)")
        return cookie


async def get_terabox_file_info(url: str, cookie: str) -> Dict:
    """
    Get file information from Terabox URL using cookie authentication.

    Args:
        url: Terabox share URL
        cookie: Terabox authentication cookie

    Returns:
        dict: File information or error
            Success: {
                'success': True,
                'file_name': str,
                'download_link': str,
                'file_size': str,
                'sizebytes': int,
                'thumbnail': str
            }
            Error: {
                'success': False,
                'error': str
            }
    """
    try:
        from TeraboxDL import TeraboxDL

        LOGGER.info(f"Getting Terabox file info for: {url}")

        # Format cookie for better compatibility
        formatted_cookie = format_cookie_for_terabox(cookie)

        # Create TeraboxDL instance
        terabox = TeraboxDL(formatted_cookie)

        # Get file info
        file_info = terabox.get_file_info(url)

        # Log the raw response for debugging
        LOGGER.info(f"TeraboxDL raw response: {file_info}")

        # Check if file_info is None
        if file_info is None:
            error_msg = "Terabox API returned None. Cookie may be invalid or link may be expired."
            LOGGER.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        # Check if file_info is not a dict
        if not isinstance(file_info, dict):
            error_msg = f"Terabox API returned unexpected type: {type(file_info).__name__}"
            LOGGER.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        # Check for errors
        if "error" in file_info:
            error_msg = file_info["error"]
            LOGGER.error(f"Terabox API error: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

        # Validate required fields
        required_fields = ['file_name', 'download_link']
        missing_fields = [field for field in required_fields if field not in file_info]
        if missing_fields:
            error_msg = f"Terabox API response missing required fields: {', '.join(missing_fields)}"
            LOGGER.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        # Validate download_link is not empty
        download_link = file_info.get('download_link', '').strip()
        if not download_link:
            error_msg = (
                "Terabox API returned empty download link. "
                "This usually means:\n"
                "1. Cookie is invalid or expired\n"
                "2. Link requires login/authentication\n"
                "3. File has been deleted or is no longer accessible\n"
                "4. Terabox API has changed\n\n"
                "Please try:\n"
                "- Update your Terabox cookie in terabox.txt\n"
                "- Verify the link is accessible in browser while logged in\n"
                "- Check if the file still exists"
            )
            LOGGER.error(error_msg)
            LOGGER.error(f"File info received: {file_info}")
            return {
                'success': False,
                'error': error_msg
            }

        # Validate sizebytes
        sizebytes = file_info.get('sizebytes', 0)
        if sizebytes == 0:
            LOGGER.warning(f"Terabox file size is 0 bytes, this may indicate an issue")
            LOGGER.warning(f"File info: {file_info}")

        # Return success with file info
        LOGGER.info(f"Terabox file info retrieved: {file_info.get('file_name', 'Unknown')}")
        LOGGER.info(f"Download link: {download_link[:100]}...")
        LOGGER.info(f"File size: {sizebytes} bytes")
        return {
            'success': True,
            **file_info
        }
        
    except ImportError:
        error_msg = "TeraboxDL library not installed. Please install: pip install terabox-downloader"
        LOGGER.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Error getting Terabox file info: {str(e)}"
        LOGGER.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }


async def download_terabox_file(
    file_info: Dict,
    save_path: str,
    cookie: str,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Download file from Terabox using file info and cookie.
    
    Args:
        file_info: File information from get_terabox_file_info()
        save_path: Directory to save the file
        cookie: Terabox authentication cookie
        progress_callback: Optional callback for progress updates
                          Signature: callback(downloaded_bytes, total_bytes, percentage)
        
    Returns:
        dict: Download result
            Success: {
                'success': True,
                'file_path': str
            }
            Error: {
                'success': False,
                'error': str
            }
    """
    try:
        from TeraboxDL import TeraboxDL

        # Ensure save_path exists
        os.makedirs(save_path, exist_ok=True)

        LOGGER.info(f"Downloading Terabox file to: {save_path}")

        # Format cookie for better compatibility
        formatted_cookie = format_cookie_for_terabox(cookie)

        # Create TeraboxDL instance
        terabox = TeraboxDL(formatted_cookie)
        
        # Download file
        result = terabox.download(
            file_info,
            save_path=save_path,
            callback=progress_callback
        )
        
        # Check for errors
        if "error" in result:
            error_msg = result["error"]
            LOGGER.error(f"Terabox download error: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
        
        # Return success
        file_path = result.get("file_path", "")
        LOGGER.info(f"Terabox file downloaded successfully: {file_path}")
        return {
            'success': True,
            'file_path': file_path
        }
        
    except ImportError:
        error_msg = "TeraboxDL library not installed. Please install: pip install terabox-downloader"
        LOGGER.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Error downloading Terabox file: {str(e)}"
        LOGGER.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }


class TeraboxDownloader:
    """
    Terabox downloader class for integration with bot's download pipeline.
    """
    
    def __init__(self, url: str, path: str, listener):
        """
        Initialize Terabox downloader.
        
        Args:
            url: Terabox share URL
            path: Download directory path
            listener: TaskListener instance
        """
        self.url = url
        self.path = path
        self.listener = listener
        self.cookie = None
        self.file_info = None
        self.is_cancelled = False
        
    async def download(self):
        """
        Execute Terabox download.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            LOGGER.info(f"[Terabox] Starting download process for: {self.url}")

            # Read cookie
            LOGGER.info("[Terabox] Reading cookie...")
            self.cookie = await read_terabox_cookie()
            if not self.cookie:
                error_msg = (
                    "Terabox cookie not found. Please add your cookie to terabox.txt file.\n\n"
                    "How to get cookie:\n"
                    "1. Login to Terabox in Edge browser\n"
                    "2. Click padlock icon → Permissions → Cookies\n"
                    "3. Copy 'lang' and 'ndus' cookie values\n"
                    "4. Format: lang=en; ndus=your_value;\n"
                    "5. Save to terabox.txt in bot root directory"
                )
                LOGGER.error("[Terabox] Cookie not found!")
                await self.listener.on_download_error(error_msg)
                return False

            LOGGER.info(f"[Terabox] Cookie loaded successfully (length: {len(self.cookie)})")

            # Get file info
            LOGGER.info(f"[Terabox] Getting file info for: {self.url}")
            info_result = await get_terabox_file_info(self.url, self.cookie)

            LOGGER.info(f"[Terabox] File info result: {info_result.get('success', False)}")

            if not info_result.get('success'):
                error = info_result.get('error', 'Unknown error')
                LOGGER.error(f"[Terabox] Failed to get file info: {error}")
                await self.listener.on_download_error(f"Terabox error: {error}")
                return False

            self.file_info = info_result

            # Set listener name and size
            self.listener.name = info_result.get('file_name', 'Unknown')
            self.listener.size = info_result.get('sizebytes', 0)

            LOGGER.info(f"[Terabox] File name: {self.listener.name}")
            LOGGER.info(f"[Terabox] File size: {self.listener.size} bytes")

            # Notify download start
            LOGGER.info("[Terabox] Notifying download start...")
            await self.listener.on_download_start()

            # Download file with progress callback
            def progress_callback(downloaded, total, percentage):
                """Progress callback for download updates."""
                if self.is_cancelled:
                    raise Exception("Download cancelled by user")
                # Update listener progress
                self.listener.subsize = downloaded
                self.listener.subname = self.listener.name

            LOGGER.info(f"[Terabox] Starting file download: {self.listener.name}")
            download_result = await download_terabox_file(
                self.file_info,
                self.path,
                self.cookie,
                progress_callback
            )

            LOGGER.info(f"[Terabox] Download result: {download_result.get('success', False)}")

            if not download_result.get('success'):
                error = download_result.get('error', 'Unknown error')
                LOGGER.error(f"[Terabox] Download failed: {error}")
                await self.listener.on_download_error(f"Download failed: {error}")
                return False

            # Download complete
            LOGGER.info(f"[Terabox] Download completed successfully: {self.listener.name}")
            await self.listener.on_download_complete()
            return True

        except Exception as e:
            import traceback
            LOGGER.error(f"[Terabox] Exception occurred: {e}")
            LOGGER.error(f"[Terabox] Traceback: {traceback.format_exc()}")
            await self.listener.on_download_error(str(e))
            return False
    
    def cancel(self):
        """Cancel the download."""
        self.is_cancelled = True
        LOGGER.info(f"Terabox download cancelled: {self.url}")


# ============================================================================
# FILE WATCHER FOR AUTOMATIC COOKIE SYNC
# ============================================================================

class TeraboxCookieWatcher:
    """
    File watcher for automatic Terabox cookie synchronization.
    Monitors terabox.txt for changes and syncs to database.
    """

    def __init__(self):
        self.cookie_file = Path("terabox.txt")
        self.is_running = False
        self.last_hash = None

    async def start(self):
        """Start the file watcher."""
        if self.is_running:
            LOGGER.warning("Cookie watcher is already running")
            return

        self.is_running = True
        LOGGER.info("🔍 Starting Terabox cookie file watcher...")

        # Initial sync on startup
        await self.check_and_sync()

        # Start periodic check task
        create_task(self._periodic_check())

        LOGGER.info("✅ Terabox cookie file watcher started")

    async def stop(self):
        """Stop the file watcher."""
        self.is_running = False
        LOGGER.info("Terabox cookie file watcher stopped")

    async def check_and_sync(self) -> bool:
        """
        Check if cookie file has changed and sync to database.

        Returns:
            bool: True if synced, False otherwise
        """
        try:
            # Check if file exists
            if not await aiopath.exists(self.cookie_file):
                LOGGER.debug("Cookie file not found, skipping sync")
                return False

            # Read cookie from file
            async with aiopen(self.cookie_file, 'r') as f:
                cookie = await f.read()
                cookie = cookie.strip()

            if not cookie:
                LOGGER.debug("Cookie file is empty, skipping sync")
                return False

            # Calculate hash
            current_hash = hashlib.sha256(cookie.encode()).hexdigest()

            # Check if changed
            if self.last_hash == current_hash:
                return False

            # Cookie has changed, sync to database
            LOGGER.info(f"🔄 Cookie file changed detected (hash: {current_hash[:16]}...)")
            success = await save_terabox_cookie_to_db(cookie, source='file')

            if success:
                self.last_hash = current_hash
                LOGGER.info("✅ Cookie synced to database successfully")
                return True
            else:
                LOGGER.error("❌ Failed to sync cookie to database")
                return False

        except Exception as e:
            LOGGER.error(f"Error checking cookie file: {e}")
            return False

    async def _periodic_check(self):
        """Periodic check for file changes (every 5 seconds)."""
        LOGGER.info("Starting periodic cookie file check (every 5 seconds)")

        while self.is_running:
            try:
                await sleep(5)  # Check every 5 seconds
                await self.check_and_sync()
            except Exception as e:
                LOGGER.error(f"Error in periodic check: {e}")
                await sleep(5)  # Continue checking even if error occurs


# Global watcher instance
_cookie_watcher = None


async def start_cookie_watcher():
    """Start the global cookie watcher."""
    global _cookie_watcher

    if _cookie_watcher is None:
        _cookie_watcher = TeraboxCookieWatcher()

    await _cookie_watcher.start()


async def stop_cookie_watcher():
    """Stop the global cookie watcher."""
    global _cookie_watcher

    if _cookie_watcher:
        await _cookie_watcher.stop()


async def manual_sync_cookie() -> Dict[str, any]:
    """
    Manually sync cookie from file to database.
    Used by /synccookie command.

    Returns:
        dict: Sync result with status and message
    """
    try:
        cookie_file = Path("terabox.txt")

        # Check if file exists
        if not await aiopath.exists(cookie_file):
            return {
                'success': False,
                'message': "Cookie file 'terabox.txt' not found"
            }

        # Read cookie from file
        async with aiopen(cookie_file, 'r') as f:
            cookie = await f.read()
            cookie = cookie.strip()

        if not cookie:
            return {
                'success': False,
                'message': "Cookie file is empty"
            }

        # Calculate hash
        cookie_hash = hashlib.sha256(cookie.encode()).hexdigest()

        # Get database metadata
        db_metadata = await get_cookie_metadata_from_db()

        # Check if already up-to-date
        if db_metadata and db_metadata.get('hash') == cookie_hash:
            return {
                'success': True,
                'message': "Cookie is already up-to-date in database",
                'cookie_preview': cookie[:50] + "...",
                'hash': cookie_hash[:16],
                'already_synced': True
            }

        # Sync to database
        success = await save_terabox_cookie_to_db(cookie, source='command')

        if success:
            return {
                'success': True,
                'message': "Cookie synced to database successfully",
                'cookie_preview': cookie[:50] + "...",
                'hash': cookie_hash[:16],
                'already_synced': False
            }
        else:
            return {
                'success': False,
                'message': "Failed to save cookie to database"
            }

    except Exception as e:
        LOGGER.error(f"Error in manual cookie sync: {e}")
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

