import re
import sys

from rich.panel import Panel
from rich import print

import utils


configuration = utils.parse_cli_arguments()


if configuration["DRY_RUN"]:
    utils.log.info("DRYRUN mode is on")

GENERIC = utils.read_file_lines("scripts/generic")
THEMING = utils.read_file_lines("scripts/theming")
REPOS = utils.read_file_lines("scripts/repos")

system_info = utils.get_system_info()
zram_state = utils.get_zram_state()
zswap_state = utils.get_zswap_state()

TWEAK_LIST = [
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
    utils.log.warning("Warning not copied exactly.")
    sys.exit()

utils.log.info(
    f'USERNAME: "{system_info["username"]}"\nRAM AMOUNT: {system_info["phys_mem_gb"]}\nCALCULATED SWAPPINESS: {system_info["swappiness"]}\nCALCULATED '
    f"VFS_CACHE_PRESSURE: {system_info['vfs_cache_pressure']}"
)

whisker_menu_path = utils.term(
    "ls " + system_info["homedir"] + "/.config/xfce4/panel/whiskermenu-*.rc"
).replace("\n", "")

# Copy system configs for necessary modifications
utils.term("cp /etc/makepkg.conf ./etc/makepkg.conf")
utils.term("cp /etc/pacman.conf ./etc/pacman.conf")
utils.term("cp /etc/mkinitcpio.conf ./etc/mkinitcpio.conf")

FILE_LIST = utils.return_files("./etc/")

# Modify configuration files
try:
    # Use all cores for makepkg
    utils.replace_in_file(
        "./etc/makepkg.conf", '#MAKEFLAGS="-j2"', 'MAKEFLAGS="-j$(nproc)"'
    )

    # Clear and Add header to 99-JomOS-settings.conf
    utils.write_file("./etc/sysctl.d/99-JomOS-settings.conf", "")
    utils.write_file(
        "./etc/sysctl.d/99-JomOS-settings.conf",
        "# This config file contains tweaks from JomOS and CachyOS\n\n",
    )

    # Apply tweaks from TWEAK_LIST
    for tweak in TWEAK_LIST:
        utils.append_to_file("./etc/sysctl.d/99-JomOS-settings.conf", tweak + "\n")
        utils.log.info(f"Added tweak: {tweak}")

    # Edit mkinitcpio.conf to use zstd compression and compression level 2
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

except Exception:
    # TODO: proper error handling
    utils.log.error("Error when modifying configurations")
else:
    utils.log.info("File ./etc/sysctl.d/99-JomOS-settings.conf modified")
    utils.log.info("File ./etc/makepkg.conf modified")
    utils.log.info("File ./etc/mkinitcpio.conf modified")
    utils.log.info("File ./etc/pacman.conf modified")


if not configuration["DRY_RUN"]:

    for file in FILE_LIST:
        file_contents = utils.read_file(file)
        # Check file length, don't show it if it's longer than 2000 characters
        if len(file_contents) < 2000:
            utils.log.info(f"Installed file: {file}\n{file_contents}")
        else:
            utils.log.info("Installed file: " + file + "\n(File too long to display)")

    # Generic commands that aren't specific to anything
    for command in GENERIC:
        utils.log.info("Executing command: " + command)
        utils.term(command)

    # Adding third party repositories
    if configuration["THIRD_PARTY_REPOS"]:
        for command in REPOS:
            utils.log.info("Executing command: " + command)
            utils.term(command)

    # Theming
    if configuration["THEMING"]:
        for command in THEMING:
            utils.log.info("Executing command: " + command)
            utils.term(command)
        if whisker_menu_path:
            utils.replace_in_file(
                str(whisker_menu_path),
                "button-title=EndeavourOS",
                "button-title=JomOS",
            )

    for tweak in TWEAK_LIST:
        utils.log.info(tweak)

    utils.install_dir("./etc", "/", "-D -o root -g root -m 644")

    utils.log.info("Please run sudo pacman -Syuu and reboot to complete installation.")
