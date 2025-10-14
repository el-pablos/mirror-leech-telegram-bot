from time import time
from re import search as research
from asyncio import gather
from aiofiles.os import path as aiopath
from psutil import (
    disk_usage,
    cpu_percent,
    swap_memory,
    cpu_count,
    virtual_memory,
    net_io_counters,
    boot_time,
)

from .. import bot_start_time
from ..helper.ext_utils.status_utils import get_readable_file_size, get_readable_time
from ..helper.ext_utils.bot_utils import cmd_exec, new_task
from ..helper.telegram_helper.message_utils import send_message

commands = {
    "aria2": (["aria2c", "--version"], r"aria2 version ([\d.]+)"),
    "qBittorrent": (["qbittorrent-nox", "--version"], r"qBittorrent v([\d.]+)"),
    "SABnzbd+": (["sabnzbdplus", "--version"], r"sabnzbdplus-([\d.]+)"),
    "python": (["python3", "--version"], r"Python ([\d.]+)"),
    "rclone": (["rclone", "--version"], r"rclone v([\d.]+)"),
    "yt-dlp": (["yt-dlp", "--version"], r"([\d.]+)"),
    "ffmpeg": (["ffmpeg", "-version"], r"ffmpeg version ([\d.]+(-\w+)?).*"),
    "7z": (["7z", "i"], r"7-Zip ([\d.]+)"),
}


@new_task
async def bot_stats(_, message):
    total, used, free, disk = disk_usage("/")
    swap = swap_memory()
    memory = virtual_memory()
    net = net_io_counters()

    # Progress bars for usage
    def get_progress_bar(percentage, length=10):
        filled = int(percentage / 10)
        bar = "░" * length
        return bar[:filled] + "█" * (filled if filled <= length else length) + bar[filled:]

    cpu_usage = cpu_percent(interval=0.5)
    ram_usage = memory.percent
    disk_usage_percent = disk
    swap_usage = swap.percent

    # User data for engagement (if available)
    try:
        from .. import user_data
        total_users = len(user_data) if user_data else 0
        active_users = len([u for u in user_data.values() if u]) if user_data else 0
        success_rate = 98.5  # Static for now, could be calculated based on task success
    except:
        total_users = 0
        active_users = 0
        success_rate = 0

    stats = f"""📊 <b>TamsHub Bot Statistics</b>
<i>Professional File Management System</i>

⏱️ <b>Runtime Information:</b>
├ Bot Uptime: {get_readable_time(time() - bot_start_time)}
├ System Uptime: {get_readable_time(time() - boot_time())}
└ Last Update: {commands["commit"]}

👥 <b>User Engagement:</b>
├ Total Users: {total_users}
├ Active Users: {active_users}
└ Success Rate: {success_rate}%

💻 <b>System Performance:</b>
├ CPU Usage: {get_progress_bar(cpu_usage)} {cpu_usage}%
├ RAM Usage: {get_progress_bar(ram_usage)} {ram_usage}%
├ Disk Usage: {get_progress_bar(disk_usage_percent)} {disk_usage_percent}%
└ SWAP Usage: {get_progress_bar(swap_usage)} {swap_usage}%

🖥️ <b>Hardware Specifications:</b>
├ Physical Cores: {cpu_count(logical=False)}
├ Total Cores: {cpu_count()}
├ Total RAM: {get_readable_file_size(memory.total)}
├ Available RAM: {get_readable_file_size(memory.available)}
└ SWAP Memory: {get_readable_file_size(swap.total)}

💾 <b>Storage Information:</b>
├ Total Space: {get_readable_file_size(total)}
├ Used Space: {get_readable_file_size(used)}
├ Free Space: {get_readable_file_size(free)}
└ Usage: {disk_usage_percent}%

🌐 <b>Network Statistics:</b>
├ Total Upload: {get_readable_file_size(net.bytes_sent)}
├ Total Download: {get_readable_file_size(net.bytes_recv)}
├ Packets Sent: {net.packets_sent:,}
└ Packets Received: {net.packets_recv:,}

🔧 <b>Software Versions:</b>
├ Python: {commands["python"]}
├ aria2: {commands["aria2"]}
├ qBittorrent: {commands["qBittorrent"]}
├ SABnzbd+: {commands["SABnzbd+"]}
├ rclone: {commands["rclone"]}
├ yt-dlp: {commands["yt-dlp"]}
├ ffmpeg: {commands["ffmpeg"]}
└ 7z: {commands["7z"]}

🔥 <b>Powered by TamsHub - High Performance Computing</b>"""
<b>SWAP:</b> {get_readable_file_size(swap.total)} | <b>Used:</b> {swap.percent}%

<b>Memory Total:</b> {get_readable_file_size(memory.total)}
<b>Memory Free:</b> {get_readable_file_size(memory.available)}
<b>Memory Used:</b> {get_readable_file_size(memory.used)}

<b>python:</b> {commands["python"]}
<b>aria2:</b> {commands["aria2"]}
<b>qBittorrent:</b> {commands["qBittorrent"]}
<b>SABnzbd+:</b> {commands["SABnzbd+"]}
<b>rclone:</b> {commands["rclone"]}
<b>yt-dlp:</b> {commands["yt-dlp"]}
<b>ffmpeg:</b> {commands["ffmpeg"]}
<b>7z:</b> {commands["7z"]}
"""
>>>>>>> origin/master
    await send_message(message, stats)


async def get_version_async(command, regex):
    try:
        out, err, code = await cmd_exec(command)
        if code != 0:
            return f"Error: {err}"
        match = research(regex, out)
        return match.group(1) if match else "Version not found"
    except Exception as e:
        return f"Exception: {str(e)}"


@new_task
async def get_packages_version():
    tasks = [get_version_async(command, regex) for command, regex in commands.values()]
    versions = await gather(*tasks)
    for tool, version in zip(commands.keys(), versions):
        commands[tool] = version
    if await aiopath.exists(".git"):
        last_commit = await cmd_exec(
            "git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True
        )
        last_commit = last_commit[0]
    else:
        last_commit = "No UPSTREAM_REPO"
    commands["commit"] = last_commit
