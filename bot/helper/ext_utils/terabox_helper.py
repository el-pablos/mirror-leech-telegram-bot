"""
Terabox download helper with cookie-based authentication.
Supports downloading files from Terabox/1024tera using user cookies.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Callable
from aiofiles import open as aiopen
from aiofiles.os import path as aiopath

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


async def read_terabox_cookie() -> Optional[str]:
    """
    Read Terabox cookie with fallback mechanism.
    Priority: Database > File

    Returns:
        str: Cookie string if found, None otherwise
    """
    # Try database first
    cookie = await read_terabox_cookie_from_db()
    if cookie:
        return cookie

    # Fallback to file
    cookie = await read_terabox_cookie_from_file()
    if cookie:
        # Save to database for future use
        await save_terabox_cookie_to_db(cookie)
        return cookie

    return None


async def save_terabox_cookie_to_db(cookie: str) -> bool:
    """
    Save Terabox cookie to MongoDB database.

    Args:
        cookie: Cookie string to save

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
            {"$set": {"terabox_cookie": cookie}},
            upsert=True
        )

        LOGGER.info("Terabox cookie saved to database")
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

        # Create TeraboxDL instance
        terabox = TeraboxDL(cookie)

        # Get file info
        file_info = terabox.get_file_info(url)

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

        # Return success with file info
        LOGGER.info(f"Terabox file info retrieved: {file_info.get('file_name', 'Unknown')}")
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
        
        # Create TeraboxDL instance
        terabox = TeraboxDL(cookie)
        
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

