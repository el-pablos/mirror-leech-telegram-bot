from time import time

from ..helper.ext_utils.bot_utils import new_task
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.telegram_helper.message_utils import send_message, edit_message, send_file
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands


@new_task
async def start(_, message):
    buttons = ButtonMaker()
    buttons.url_button(
        "Repo", "https://www.github.com/anasty17/mirror-leech-telegram-bot"
    )
    buttons.url_button("Code Owner", "https://t.me/anas_tayyar")
    reply_markup = buttons.build_menu(2)
    if await CustomFilters.authorized(_, message):
        start_string = f"""
This bot can mirror from links|tgfiles|torrents|nzb|rclone-cloud to any rclone cloud, Google Drive or to telegram.
Type /{BotCommands.HelpCommand} to get a list of available commands
"""
        await send_message(message, start_string, reply_markup)
    else:
        await send_message(
            message,
            "This bot can mirror from links|tgfiles|torrents|nzb|rclone-cloud to any rclone cloud, Google Drive or to telegram.\n\n⚠️ You Are not authorized user! Deploy your own mirror-leech bot",
            reply_markup,
        )


@new_task
async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await send_message(message, "⚡ Starting TamsHub Network Test...")
    end_time = int(round(time() * 1000))
    ping_ms = end_time - start_time

    # Update with ping result first
    await edit_message(reply, f"⚡ Running comprehensive network test...\n📍 Ping: {ping_ms} ms")

    # Run speedtest
    try:
        from ..helper.ext_utils.bot_utils import cmd_exec
        import asyncio

        # Multiple speedtest methods for reliability
        speedtest_result = None

        # Method 1: Try speedtest-cli
        try:
            out, err, code = await cmd_exec("speedtest-cli --simple --timeout 45")
            if code == 0 and out:
                lines = out.strip().split('\n')
                download_speed = ""
                upload_speed = ""
                ping_speedtest = ""

                for line in lines:
                    if "Download:" in line:
                        download_speed = line.split("Download: ")[1].strip()
                    elif "Upload:" in line:
                        upload_speed = line.split("Upload: ")[1].strip()
                    elif "Ping:" in line:
                        ping_speedtest = line.split("Ping: ")[1].strip()

                if download_speed and upload_speed:
                    speedtest_result = {
                        "download": download_speed,
                        "upload": upload_speed,
                        "ping": ping_speedtest or f"{ping_ms} ms"
                    }
        except Exception as e:
            pass

        # Method 2: Fallback to curl-based tests if speedtest-cli fails
        if not speedtest_result:
            try:
                # Test multiple servers for better accuracy
                test_urls = [
                    "http://speedtest.tele2.net/10MB.zip",
                    "http://212.183.159.230/5MB.zip",
                    "http://ipv4.download.thinkbroadband.com/5MB.zip"
                ]

                best_speed = 0
                for url in test_urls:
                    try:
                        # Test download speed
                        out, err, code = await cmd_exec(f"curl -w '%{{speed_download}}' -o /dev/null -s --max-time 20 {url}")
                        if code == 0 and out.strip():
                            speed_bytes = float(out.strip())
                            if speed_bytes > best_speed:
                                best_speed = speed_bytes
                    except:
                        continue

                if best_speed > 0:
                    speed_mbps = (best_speed * 8) / (1024 * 1024)  # Convert to Mbps

                    # Simple upload test using httpbin
                    upload_speed = "N/A"
                    try:
                        out, err, code = await cmd_exec("curl -w '%{speed_upload}' -o /dev/null -s --max-time 15 -F 'file=@/dev/urandom' -X POST https://httpbin.org/post --data-urlencode 'data=test'")
                        if code == 0 and out.strip():
                            upload_bytes = float(out.strip())
                            upload_mbps = (upload_bytes * 8) / (1024 * 1024)
                            upload_speed = f"{upload_mbps:.2f} Mbit/s"
                    except:
                        pass

                    speedtest_result = {
                        "download": f"{speed_mbps:.2f} Mbit/s",
                        "upload": upload_speed,
                        "ping": f"{ping_ms} ms"
                    }
            except:
                pass

        # Method 3: Ultra-simple wget test as last resort
        if not speedtest_result:
            try:
                out, err, code = await cmd_exec("wget --timeout=15 --tries=1 -O /dev/null http://speedtest.tele2.net/1MB.zip 2>&1")
                if "saved" in out.lower() or code == 0:
                    # Extract speed from wget output
                    import re
                    speed_match = re.search(r'(\d+\.?\d*)\s*(MB/s|KB/s)', out)
                    if speed_match:
                        speed_val = float(speed_match.group(1))
                        speed_unit = speed_match.group(2)
                        if speed_unit == "KB/s":
                            speed_mbps = (speed_val * 8) / 1024  # Convert KB/s to Mbps
                        else:  # MB/s
                            speed_mbps = speed_val * 8  # Convert MB/s to Mbps

                        speedtest_result = {
                            "download": f"{speed_mbps:.2f} Mbit/s",
                            "upload": "N/A",
                            "ping": f"{ping_ms} ms"
                        }
            except:
                pass

        # Format the final message
        if speedtest_result:
            final_msg = f"""🚀 <b>TamsHub Network Performance</b>

📡 <b>Connection Test:</b>
├ 📍 Ping: {ping_ms} ms
├ 🔽 Download: {speedtest_result.get('download', 'N/A')}
├ 🔼 Upload: {speedtest_result.get('upload', 'N/A')}
└ 🌐 Server Ping: {speedtest_result.get('ping', f'{ping_ms} ms')}

⚡ <b>Status:</b> {'🟢 Excellent' if ping_ms < 100 else '🟡 Good' if ping_ms < 200 else '🔴 Poor'}
🔥 <b>TamsHub High-Speed Network</b>"""
        else:
            final_msg = f"""🚀 <b>TamsHub Network Performance</b>

📡 <b>Connection Test:</b>
├ 📍 Ping: {ping_ms} ms
├ 🔽 Download: Testing failed
├ 🔼 Upload: Testing failed
└ 🌐 Status: {'🟢 Excellent' if ping_ms < 100 else '🟡 Good' if ping_ms < 200 else '🔴 Poor'}

🔥 <b>TamsHub Network Monitor</b>"""

        await edit_message(reply, final_msg)

    except Exception as e:
        # Fallback to simple ping if speedtest fails
        final_msg = f"""🚀 <b>TamsHub Network Performance</b>

📡 <b>Connection Test:</b>
├ 📍 Ping: {ping_ms} ms
├ 🔽 Download: Test unavailable
├ 🔼 Upload: Test unavailable
└ 🌐 Status: {'🟢 Excellent' if ping_ms < 100 else '🟡 Good' if ping_ms < 200 else '🔴 Poor'}

🔥 <b>TamsHub Network Monitor</b>"""
        await edit_message(reply, final_msg)


@new_task
async def log(_, message):
    await send_file(message, "log.txt")
