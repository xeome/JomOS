import os
import re
import getpass

def get_system_info():
    username = "liveuser" if os.path.exists("/home/liveuser") else getpass.getuser()
    homedir = "/home/" + username

    system_info = {
        "username": username,
        "homedir": homedir,
        "phys_mem_raw": os.popen("grep MemTotal /proc/meminfo").read(),
    }

    system_info["phys_mem_gb"] = round(
        int(re.sub("[^0-9]", "", system_info["phys_mem_raw"])) / 1048576
    )
    system_info["swappiness"] = min((200 // system_info["phys_mem_gb"]) * 2, 150)
    system_info["vfs_cache_pressure"] = int(
        max(min(system_info["swappiness"] * 1.25, 125), 32)
    )

    return system_info


system_info = get_system_info()

SYSCTL_TWEAK_LIST = [
    "### Memory tweaks",
    f"vm.swappiness = {system_info['swappiness']}",
    f"vm.vfs_cache_pressure = {system_info['vfs_cache_pressure']}",
    "vm.page-cluster = 0",
    "vm.dirty_ratio = 10",
    "vm.dirty_background_ratio = 5\n",
    "### Network tweaks",
    "net.core.default_qdisc = cake",
    "net.ipv4.tcp_congestion_control = bbr2",
    "net.ipv4.tcp_fastopen = 3\n",
    "### Misc tweaks",
    "kernel.nmi_watchdog = 0\n",
]