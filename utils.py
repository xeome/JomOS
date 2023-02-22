import os
import re
import sys
import rich
import logging
import getpass

from rich.logging import RichHandler
from rich.panel import Panel

from rich import print

import tweaks

def setup_logging():
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    return logging.getLogger("rich")


log = setup_logging()


def parse_arguments(config, details):
    arguments = sys.argv[1:]
    for arg in arguments:
        if arg in details:
            lookup = details[arg]
            config[lookup[0]] = lookup[1]
        elif arg == "--h" or arg == "--help":
            rich.print("usage: python main.py", end="")
            for argument in details:
                rich.print(f" [--{argument}]")
            rich.print("\noptions:\n-h, --help\t show this help message and exit")
            for argument, lookup in details.items():
                rich.print(f"[--{argument}\t {lookup[2]}]")
        else:
            rich.print(f"incorrect argument {arg}\n")
            rich.print("usage: python main.py", end="")
            for argument in details:
                rich.print(f" [--{argument}]")
            rich.print("\noptions:\n-h, --help\t show this help message and exit")
            for argument, lookup in details.items():
                rich.print(f"[--{argument}\t {lookup[2]}]")


def term(str):
    """Execute a terminal command"""
    return os.popen(str).read()


def install_dir(input, target_path, flags):
    """Install a directory with necessary permissions"""
    term(
        "find "
        + input
        + " -type f -exec sudo install "
        + flags
        + ' "{}" "'
        + target_path
        + '{}" \;'
    )


def read_file(file_path):
    """Read file and return its contents"""
    with open(file_path, "r") as file:
        return file.read()


def read_file_lines(file_path):
    """Read file and return its contents as lines"""
    with open(file_path, "r") as file:
        return [x.strip() for x in file.readlines()]


def write_file(file_path, file_data):
    with open(file_path, "w") as file:
        file.write(file_data)


def return_files(file_path):
    lst = list()
    for path, _, files in os.walk(file_path):
        for name in files:
            lst.append(str(os.path.join(path, name)))
    return lst


def replace_in_file(file_path, str, sub):
    """Replace string in file"""
    with open(file_path, "r") as file:
        file_data = file.read()

    file_data = file_data.replace(str, sub)

    with open(file_path, "w") as file:
        file.write(file_data)


def append_to_file(file_path, str):
    """Append string to file"""
    with open(file_path, "a") as file:
        file.write(str)


def parse_cli_arguments():
    configuration = {
        "DRY_RUN": 1,
        "THIRD_PARTY_REPOS": 1,
        "THEMING": 1,
    }

    cli_args = {
        "disable_repos": [
            "THIRD_PARTY_REPOS",
            0,
            "disables usage of third party repos",
        ],
        "disable_theming": ["THEMING", 0, "disables theming of the OS"],
        "enable_dry_run": ["DRY_RUN", 1, "does a dry run of the program"],
    }

    parse_arguments(configuration, cli_args)

    return configuration

def get_zram_state():
    zram_state = term("swapon -s")
    if zram_state.find("zram") != -1:
        log.info("This system already has zram")
    elif zram_state.find("dev") != -1:
        log.info("This system already has physical swap")
    else:
        log.info("System has no swap")
    return zram_state


def get_zswap_state():
    zswap_state = term("cat /sys/module/zswap/parameters/enabled")
    if zswap_state == "N\n":
        log.info("Zswap is disabled")
    else:
        log.warning("Zswap is enabled, please disable Zswap if you want to use zram.")
    return zswap_state


def confirm_to_proceed():
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


# Copy system configs for necessary modifications
def copy_configs():
    term("cp /etc/makepkg.conf ./etc/makepkg.conf")
    term("cp /etc/pacman.conf ./etc/pacman.conf")
    term("cp /etc/mkinitcpio.conf ./etc/mkinitcpio.conf")


# Modify configuration files
def modify_configs():
    try:
    # Use all cores for makepkg
        replace_in_file(
        "./etc/makepkg.conf", '#MAKEFLAGS="-j2"', 'MAKEFLAGS="-j$(nproc)"'
    )

    # Clear and Add header to 99-JomOS-settings.conf
        write_file("./etc/sysctl.d/99-JomOS-settings.conf", "")
        write_file(
        "./etc/sysctl.d/99-JomOS-settings.conf",
        "# This config file contains tweaks from JomOS and CachyOS\n\n",
    )

    # Apply tweaks from SYSCTL_TWEAK_LIST
        for tweak in tweaks.SYSCTL_TWEAK_LIST:
            append_to_file("./etc/sysctl.d/99-JomOS-settings.conf", tweak + "\n")
            log.info(f"Added tweak: {tweak}")

    # Edit mkinitcpio.conf to use zstd compression and compression level 2
        mkinitcpio = read_file("./etc/mkinitcpio.conf")
        if (
        mkinitcpio.find("COMPRESSION") == 0
        and mkinitcpio.find("#COMPRESSION_OPTIONS") == 0
    ):
            mkinitcpio = re.sub(
            'COMPRESSION="(.*?)"', 'COMPRESSION="zstd"', str(mkinitcpio)
        )
            mkinitcpio.replace("#COMPRESSION_OPTIONS=()", "COMPRESSION_OPTIONS=(-2)")

        write_file("./etc/mkinitcpio.conf", mkinitcpio)

    except Exception:
    # TODO: proper error handling
        log.error("Error when modifying configurations")
    else:
        log.info("File ./etc/sysctl.d/99-JomOS-settings.conf modified")
        log.info("File ./etc/makepkg.conf modified")
        log.info("File ./etc/mkinitcpio.conf modified")
        log.info("File ./etc/pacman.conf modified")


def apply_tweaks(configuration, GENERIC, THEMING, REPOS, system_info):
    if not configuration["DRY_RUN"]:
        FILE_LIST = return_files("./etc/")
        for file in FILE_LIST:
            file_contents = read_file(file)
        # Check file length, don't show it if it's longer than 2000 characters
            if len(file_contents) < 2000:
                log.info(f"Installed file: {file}\n{file_contents}")
            else:
                log.info("Installed file: " + file + "\n(File too long to display)")

    # Generic commands that aren't specific to anything
        for command in GENERIC:
            log.info("Executing command: " + command)
            term(command)

    # Adding third party repositories
        if configuration["THIRD_PARTY_REPOS"]:
            for command in REPOS:
                log.info("Executing command: " + command)
                term(command)

    # Theming
        if configuration["THEMING"]:
            for command in THEMING:
                log.info("Executing command: " + command)
                term(command)
            whisker_menu_path = term(
            "ls " + system_info["homedir"] + "/.config/xfce4/panel/whiskermenu-*.rc"
        ).replace("\n", "")
            if whisker_menu_path:
                replace_in_file(
                str(whisker_menu_path),
                "button-title=EndeavourOS",
                "button-title=JomOS",
            )

        for tweak in tweaks.SYSCTL_TWEAK_LIST:
            log.info(tweak)

        install_dir("./etc", "/", "-D -o root -g root -m 644")

        log.info("Please run sudo pacman -Syuu and reboot to complete installation.")
