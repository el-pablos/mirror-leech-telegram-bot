from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage
from time import time
from asyncio import iscoroutinefunction, gather

from ... import task_dict, task_dict_lock, bot_start_time, status_dict, DOWNLOAD_DIR
from ...core.config_manager import Config
from ..telegram_helper.button_build import ButtonMaker

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


class MirrorStatus:
    STATUS_UPLOAD = "Upload"
    STATUS_DOWNLOAD = "Download"
    STATUS_CLONE = "Clone"
    STATUS_QUEUEDL = "QueueDl"
    STATUS_QUEUEUP = "QueueUp"
    STATUS_PAUSED = "Pause"
    STATUS_ARCHIVE = "Archive"
    STATUS_EXTRACT = "Extract"
    STATUS_SPLIT = "Split"
    STATUS_CHECK = "CheckUp"
    STATUS_SEED = "Seed"
    STATUS_SAMVID = "SamVid"
    STATUS_CONVERT = "Convert"
    STATUS_FFMPEG = "FFmpeg"


STATUSES = {
    "ALL": "All",
    "DL": MirrorStatus.STATUS_DOWNLOAD,
    "UP": MirrorStatus.STATUS_UPLOAD,
    "QD": MirrorStatus.STATUS_QUEUEDL,
    "QU": MirrorStatus.STATUS_QUEUEUP,
    "AR": MirrorStatus.STATUS_ARCHIVE,
    "EX": MirrorStatus.STATUS_EXTRACT,
    "SD": MirrorStatus.STATUS_SEED,
    "CL": MirrorStatus.STATUS_CLONE,
    "CM": MirrorStatus.STATUS_CONVERT,
    "SP": MirrorStatus.STATUS_SPLIT,
    "SV": MirrorStatus.STATUS_SAMVID,
    "FF": MirrorStatus.STATUS_FFMPEG,
    "PA": MirrorStatus.STATUS_PAUSED,
    "CK": MirrorStatus.STATUS_CHECK,
}


async def get_task_by_gid(gid: str):
    async with task_dict_lock:
        for tk in task_dict.values():
            if hasattr(tk, "seeding"):
                await tk.update()
            if tk.gid() == gid:
                return tk
        return None


async def get_specific_tasks(status, user_id):
    if status == "All":
        if user_id:
            return [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        else:
            return list(task_dict.values())
    tasks_to_check = (
        [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        if user_id
        else list(task_dict.values())
    )
    coro_tasks = []
    coro_tasks.extend(tk for tk in tasks_to_check if iscoroutinefunction(tk.status))
    coro_statuses = await gather(*[tk.status() for tk in coro_tasks])
    result = []
    coro_index = 0
    for tk in tasks_to_check:
        if tk in coro_tasks:
            st = coro_statuses[coro_index]
            coro_index += 1
        else:
            st = tk.status()
        if (st == status) or (
            status == MirrorStatus.STATUS_DOWNLOAD and st not in STATUSES.values()
        ):
            result.append(tk)
    return result


async def get_all_tasks(req_status: str, user_id):
    async with task_dict_lock:
        return await get_specific_tasks(req_status, user_id)


def get_readable_file_size(size_in_bytes):
    if not size_in_bytes:
        return "0B"

    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"


def get_readable_time(seconds: int):
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result


def time_to_seconds(time_duration):
    try:
        parts = time_duration.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(float, parts)
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = float(parts[0])
        else:
            return 0
        return hours * 3600 + minutes * 60 + seconds
    except:
        return 0


def speed_string_to_bytes(size_text: str):
    size = 0
    size_text = size_text.lower()
    if "k" in size_text:
        size += float(size_text.split("k")[0]) * 1024
    elif "m" in size_text:
        size += float(size_text.split("m")[0]) * 1048576
    elif "g" in size_text:
        size += float(size_text.split("g")[0]) * 1073741824
    elif "t" in size_text:
        size += float(size_text.split("t")[0]) * 1099511627776
    elif "b" in size_text:
        size += float(size_text.split("b")[0])
    return size


def get_progress_bar_string(pct):
    pct = float(pct.strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 5)  # Changed from 8 to 5 for smoother progress

    # Modern progress bar with gradient effect
    if p == 0:
        bar = "░" * 20
    elif p == 100:
        bar = "█" * 20
    else:
        # Create gradient effect
        filled = "█" * cFull
        partial = "▓" if cFull < 20 else ""
        empty = "░" * (20 - cFull - (1 if partial else 0))
        bar = filled + partial + empty

    return f"╭─{'─' * 20}─╮\n│{bar}│ {p:.1f}%\n╰─{'─' * 20}─╯"


async def get_readable_message(sid, is_user, page_no=1, status="All", page_step=1):
    msg = ""
    button = None

    tasks = await get_specific_tasks(status, sid if is_user else None)

    STATUS_LIMIT = Config.STATUS_LIMIT
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    start_position = (page_no - 1) * STATUS_LIMIT

    for index, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        if status != "All":
            tstatus = status
        elif iscoroutinefunction(task.status):
            tstatus = await task.status()
        else:
            tstatus = task.status()
        # Modern task header with icons
        status_icons = {
            MirrorStatus.STATUS_DOWNLOAD: "📥",
            MirrorStatus.STATUS_UPLOAD: "📤",
            MirrorStatus.STATUS_CLONE: "📋",
            MirrorStatus.STATUS_ARCHIVE: "🗃️",
            MirrorStatus.STATUS_EXTRACT: "📦",
            MirrorStatus.STATUS_SEED: "🌱",
            MirrorStatus.STATUS_QUEUEDL: "⏳",
            MirrorStatus.STATUS_QUEUEUP: "⏳",
            MirrorStatus.STATUS_PAUSED: "⏸️",
            MirrorStatus.STATUS_CONVERT: "🔄",
            MirrorStatus.STATUS_FFMPEG: "🎬",
            MirrorStatus.STATUS_SPLIT: "✂️"
        }

        icon = status_icons.get(tstatus, "📁")

        if task.listener.is_super_chat:
            msg += f"╭─ {icon} <b><a href='{task.listener.message.link}'>{tstatus}</a></b> #{index + start_position}\n"
        else:
            msg += f"╭─ {icon} <b>{tstatus}</b> #{index + start_position}\n"

        msg += f"├ 📄 <code>{escape(f'{task.name()}')}</code>\n"
        if task.listener.subname:
            msg += f"├ 📁 <i>{task.listener.subname}</i>\n"

        if (
            tstatus not in [MirrorStatus.STATUS_SEED, MirrorStatus.STATUS_QUEUEUP]
            and task.listener.progress
        ):
            progress = task.progress()
            msg += f"├\n{get_progress_bar_string(progress)}\n├\n"

            if task.listener.subname:
                subsize = f"/{get_readable_file_size(task.listener.subsize)}"
                ac = len(task.listener.files_to_proceed)
                count = f"{task.listener.proceed_count}/{ac or '?'}"
            else:
                subsize = ""
                count = ""

            msg += f"├ 📊 <b>Processed:</b> {task.processed_bytes()}{subsize}\n"
            if count:
                msg += f"├ 🔢 <b>Count:</b> {count}\n"
            msg += f"├ 📏 <b>Size:</b> {task.size()}\n"
            msg += f"├ ⚡ <b>Speed:</b> {task.speed()}\n"
            msg += f"├ ⏱️ <b>ETA:</b> {task.eta()}\n"

            if (
                tstatus == MirrorStatus.STATUS_DOWNLOAD
                and task.listener.is_torrent
                or task.listener.is_qbit
            ):
                try:
                    msg += f"├ 🌱 <b>Seeders:</b> {task.seeders_num()} | 🔽 <b>Leechers:</b> {task.leechers_num()}\n"
                except:
                    pass
        elif tstatus == MirrorStatus.STATUS_SEED:
            msg += f"├ 📏 <b>Size:</b> {task.size()}\n"
            msg += f"├ ⚡ <b>Speed:</b> {task.seed_speed()}\n"
            msg += f"├ 📤 <b>Uploaded:</b> {task.uploaded_bytes()}\n"
            msg += f"├ ⚖️ <b>Ratio:</b> {task.ratio()}\n"
            msg += f"├ ⏰ <b>Time:</b> {task.seeding_time()}\n"
        else:
            msg += f"├ 📏 <b>Size:</b> {task.size()}\n"

        msg += f"╰─ 🆔 <code>{task.gid()}</code>\n\n"

    if len(msg) == 0:
        if status == "All":
            return None, None
        else:
            msg = f"No Active {status} Tasks!\n\n"
    buttons = ButtonMaker()
    if not is_user:
        buttons.data_button("📜", f"status {sid} ov", position="header")
    if len(tasks) > STATUS_LIMIT:
        msg += f"<b>Page:</b> {page_no}/{pages} | <b>Tasks:</b> {tasks_no} | <b>Step:</b> {page_step}\n"
        buttons.data_button("<<", f"status {sid} pre", position="header")
        buttons.data_button(">>", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15]:
                buttons.data_button(i, f"status {sid} ps {i}", position="footer")
    if status != "All" or tasks_no > 20:
        for label, status_value in list(STATUSES.items()):
            if status_value != status:
                buttons.data_button(label, f"status {sid} st {status_value}")
    buttons.data_button("♻️", f"status {sid} ref", position="header")
    button = buttons.build_menu(8)
    # Modern system status footer with TamsHub branding
    cpu_usage = cpu_percent()
    memory = virtual_memory()
    free_space = get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)
    uptime = get_readable_time(time() - bot_start_time)

    def get_mini_bar(percentage, length=8):
        filled = int(percentage / 100 * length)
        return "█" * filled + "░" * (length - filled)

    msg += f"""╭─ 💻 <b>TamsHub System Monitor</b> ─╮
├ 🖥️ CPU: {get_mini_bar(cpu_usage)} {cpu_usage:.1f}%
├ 🧠 RAM: {get_mini_bar(memory.percent)} {memory.percent:.1f}%
├ 💾 FREE: {free_space}
╰─ ⏰ UPTIME: {uptime} ─╯"""
    return msg, button
