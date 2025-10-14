#!/usr/bin/env python3
"""
Setup script to save Terabox and YouTube cookies to MongoDB database.
This script should be run once during Docker build or initial setup.
"""

import asyncio
import sys
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bot import LOGGER
from bot.core.config_manager import Config
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.terabox_helper import (
    save_terabox_cookie_to_db,
    save_youtube_cookie_to_db,
    read_terabox_cookie_from_file
)


async def setup_terabox_cookie():
    """Setup Terabox cookie from terabox.txt file."""
    
    print("=" * 80)
    print("SETTING UP TERABOX COOKIE")
    print("=" * 80)
    print()
    
    # Read cookie from file
    cookie = await read_terabox_cookie_from_file()
    
    if not cookie:
        print("❌ Failed to read Terabox cookie from terabox.txt")
        print("   Please make sure terabox.txt exists and contains valid cookie")
        return False
    
    print(f"✅ Terabox cookie loaded from file")
    print(f"   Cookie length: {len(cookie)} characters")
    print(f"   Cookie preview: {cookie[:80]}...")
    print()
    
    # Save to database
    if database.db is None:
        print("⚠️  Database not connected, skipping database save")
        return True
    
    success = await save_terabox_cookie_to_db(cookie)
    
    if success:
        print("✅ Terabox cookie saved to database successfully")
    else:
        print("❌ Failed to save Terabox cookie to database")
    
    print()
    return success


async def setup_youtube_cookie():
    """Setup YouTube cookie from cookies.txt file."""
    
    print("=" * 80)
    print("SETTING UP YOUTUBE COOKIE")
    print("=" * 80)
    print()
    
    cookie_file = "cookies.txt"
    
    # Check if file exists
    if not Path(cookie_file).exists():
        print(f"⚠️  YouTube cookie file not found: {cookie_file}")
        print("   Skipping YouTube cookie setup")
        print()
        return True
    
    # Read cookie file
    try:
        with open(cookie_file, 'r') as f:
            cookie_content = f.read()
        
        if not cookie_content.strip():
            print(f"⚠️  YouTube cookie file is empty: {cookie_file}")
            print("   Skipping YouTube cookie setup")
            print()
            return True
        
        print(f"✅ YouTube cookie loaded from file")
        print(f"   Cookie length: {len(cookie_content)} characters")
        print()
        
        # Save to database
        if database.db is None:
            print("⚠️  Database not connected, skipping database save")
            return True
        
        success = await save_youtube_cookie_to_db(cookie_content)
        
        if success:
            print("✅ YouTube cookie saved to database successfully")
        else:
            print("❌ Failed to save YouTube cookie to database")
        
        print()
        return success
        
    except Exception as e:
        print(f"❌ Error reading YouTube cookie file: {e}")
        print()
        return False


async def main():
    """Main setup function."""
    
    print()
    print("=" * 80)
    print("COOKIE SETUP SCRIPT")
    print("=" * 80)
    print()
    
    # Load configuration
    try:
        Config.load()
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    print()
    
    # Connect to database if DATABASE_URL is set
    if Config.DATABASE_URL:
        print("Connecting to database...")
        try:
            await database.connect()
            if database.db is not None:
                print("✅ Database connected successfully")
            else:
                print("⚠️  Database connection failed, cookies will only be available from files")
        except Exception as e:
            print(f"⚠️  Database connection error: {e}")
            print("   Cookies will only be available from files")
    else:
        print("⚠️  DATABASE_URL not set, cookies will only be available from files")
    
    print()
    
    # Setup cookies
    terabox_success = await setup_terabox_cookie()
    youtube_success = await setup_youtube_cookie()
    
    # Disconnect database
    if database.db is not None:
        await database.disconnect()
        print("Database disconnected")
        print()
    
    # Summary
    print("=" * 80)
    print("SETUP SUMMARY")
    print("=" * 80)
    print()
    print(f"Terabox Cookie: {'✅ SUCCESS' if terabox_success else '❌ FAILED'}")
    print(f"YouTube Cookie: {'✅ SUCCESS' if youtube_success else '❌ FAILED'}")
    print()
    
    if terabox_success and youtube_success:
        print("✅ All cookies setup successfully!")
    elif terabox_success or youtube_success:
        print("⚠️  Some cookies setup successfully, some failed")
    else:
        print("❌ Cookie setup failed")
    
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(main())

