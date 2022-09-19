import logging
import os
import re
import sys

from rich import print
from rich.logging import RichHandler
from rich.panel import Panel

import utils

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

# Options, TODO: make them a cli parameter
configuration = {}
configuration["DRY_RUN"] = 1
configuration["THIRD_PARTY_REPOS"] = 1
configuration["THEMING"] = 1
utils.parse_arguments(
    configuration,
    {
        "disable_repos": [
            "THIRD_PARTY_REPOS",
            0,
            "disables usage of third party repos",
        ],
        "disable_theming": ["THEMING", 0, "disables theming of the OS"],
        "enable_dry_run": ["DRY_RUN", 1, "does a dry run of the program"],
    },
)

if configuration["DRY_RUN"]:
    log.info("DRYRUN mode is on")

V3_SUPPORT = utils.term(
    '/lib/ld-linux-x86-64.so.2 --help | grep "x86-64-v3 (supported, searched)"'
).find("86-64-v3 (supported, searched)")

GENERIC = utils.read_file_lines("scripts/generic")
THEMING = utils.read_file_lines("scripts/theming")
REPOS_V3 = utils.read_file_lines("scripts/repos-v3")
REPOS = utils.read_file_lines("scripts/repos")

username = (
    "liveuser"
    if os.path.exists("/home/liveuser")
    else utils.term("whoami").replace("\n", "")
)

homedir = "/home/" + username
phys_mem_raw = utils.term("grep MemTotal /proc/meminfo")

# Get ram amount in kb and convert to gb with floor division
phys_mem_gb = int(re.sub("[^0-9]", "", phys_mem_raw)) // 1048576

swappiness = min((200 // phys_mem_gb) * 2, 150)
vfs_cache_pressure = int(max(min(swappiness * 1.25, 125), 32))


zram_state = utils.term("swapon -s")
if zram_state.find("zram") == 0:
    log.info("This system already has zram")
elif zram_state.find("dev") == 0:
    log.info("This system already has physical swap")
else:
    log.info("System has no swap")

zswap_state = utils.term("cat /sys/module/zswap/parameters/enabled")
log.info(zswap_state)

if zswap_state == "N\n":
    log.info("Zswap is disabled")
else:
    log.warning("Zswap is enabled, please disable Zswap if you want to use zram.")


TWEAK_LIST = [
    f"vm.swappiness = {swappiness}",
    f"vm.vfs_cache_pressure = {vfs_cache_pressure}",
    "vm.page-cluster = 0",
    "vm.dirty_ratio = 10",
    "vm.dirty_background_ratio = 5",
    "net.core.default_qdisc = cake",
    "net.ipv4.tcp_congestion_control = bbr2",
    "net.ipv4.tcp_fastopen = 3",
    "kernel.nmi_watchdog = 0",
]

ABOUT = """
JomOS is a meta Linux distribution which allows users to mix-and-match
well tested configurations and optimizations with little to no effort 
 
JomOS integrates these configurations into one largely cohesive system.

[red]
Continuing will:
- Convert existing installation into JomOS
[/red]
"""

print(Panel.fit(ABOUT, title="JomOS alpha 0.1"))

confirmation = input(
    'Please type "Confirm" without quotes at the prompt to continue: \n'
)

if confirmation != "Confirm":
    log.warning("Warning not copied exactly.")
    sys.exit()

log.info(
    f'USERNAME: "{username}"\nRAM AMOUNT: {phys_mem_gb}\nCALCULATED SWAPPINESS: {swappiness}\nCALCULATED '
    f"VFS_CACHE_PRESSURE: {vfs_cache_pressure} "
)

whisker_menu_path = utils.term(
    "ls " + homedir + "/.config/xfce4/panel/whiskermenu-*.rc"
).replace("\n", "")

# Copy system configs for necessary modifications
utils.term("cp /etc/makepkg.conf ./etc/makepkg.conf")
utils.term("cp /etc/pacman.conf ./etc/pacman.conf")
utils.term("cp /etc/mkinitcpio.conf ./etc/mkinitcpio.conf")

FILE_LIST = utils.return_files("./etc/")

# Modify configuration files
try:
    if not configuration["DRY_RUN"]:
        utils.replace_in_file(
            "./etc/makepkg.conf", '#MAKEFLAGS="-j2"', 'MAKEFLAGS="-j$(nproc)"'
        )

        utils.replace_in_file(
            "./etc/sysctl.d/99-JomOS-settings.conf",
            "vm.swappiness = 50",
            "vm.swappiness = " + str(swappiness),
        )

        utils.replace_in_file(
            "./etc/sysctl.d/99-JomOS-settings.conf",
            "vm.vfs_cache_pressure = 50",
            "vm.vfs_cache_pressure = " + str(vfs_cache_pressure),
        )

        mkinitcpio = utils.read_file("./etc/mkinitcpio.conf")
        if (
            mkinitcpio.find("COMPRESSION") == 0
            and mkinitcpio.find("#COMPRESSION_OPTIONS") == 0
        ):
            mkinitcpio = re.sub(
                'COMPRESSION="(.*?)"', 'COMPRESSION="zstd"', str(mkinitcpio)
            )
            mkinitcpio.replace("#COMPRESSION_OPTIONS=()", "COMPRESSION_OPTIONS=(-2)")

        utils.write_file("./etc/mkinitcpio.conf", mkinitcpio)

        if V3_SUPPORT and configuration["THIRD_PARTY_REPOS"]:
            utils.replace_in_file(
                "./etc/pacman.conf",
                "[core]\nInclude = /etc/pacman.d/mirrorlist",
                "[cachyos-v3]\nInclude = /etc/pacman.d/cachyos-v3-mirrorlist\n[cachyos]\nInclude = /etc/pacman.d/cachos-mirrorlist\n\n[core]Include = /etc/pacman.d/mirrorlist",
            )
        elif configuration["THIRD_PARTY_REPOS"]:
            utils.replace_in_file(
                "./etc/pacman.conf",
                "[core]\nInclude = /etc/pacman.d/mirrorlist",
                "[cachyos]\nInclude = /etc/pacman.d/cachyos-mirrorlist\n\n[core]\nInclude = /etc/pacman.d/mirrorlist",
            )

except Exception:
    # TODO: proper error handling
    log.error("Error when modifying configurations")
else:
    log.info("File /etc/sysctl.d/99-JomOS-settings.conf modified")
    log.info("File /etc/makepkg.conf modified")
    log.info("File /etc/mkinitcpio.conf modified")
    log.info("File /etc/pacman.conf modified")

if V3_SUPPORT:
    log.info("86-64-v3 (supported, searched)")

if not configuration["DRY_RUN"]:

    for file in FILE_LIST:
        file_contents = utils.read_file(file)
        # Check file length, don't show it if it's longer than 2000 characters
        if len(file_contents) < 2000:
            log.info(f"Installed file: {file}\n{file_contents}")
        else:
            log.info("Installed file: " + file + "\n(File too long to display)")

    # Generic commands that aren't specific to anything
    for command in GENERIC:
        log.info("Executing command: " + command)
        utils.term(command)

    # Adding third party repositories
    if V3_SUPPORT and ENABLE_THIRD_PARTY_REPOS:
        for command in REPOS_V3:
            log.info("Executing command: " + command)
            utils.term(command)
    elif ENABLE_THIRD_PARTY_REPOS:
        for command in REPOS:
            log.info("Executing command: " + command)
            utils.term(command)

    # Theming
    if configuration["THEMING"]:
        for command in THEMING:
            log.info("Executing command: " + command)
            utils.term(command)

    for tweak in TWEAK_LIST:
        log.info(tweak)

    utils.install_dir("./etc", "/", "-D -o root -g root -m 644")

    if whisker_menu_path and configuration["THEMING"]:
        utils.replace_in_file(
            str(whisker_menu_path),
            "button-title=EndeavourOS",
            "button-title=JomOS",
        )
