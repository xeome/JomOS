import os
import re
import sys
import rich
import logging
import getpass

from rich.logging import RichHandler


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


def get_system_info():
    username = "liveuser" if os.path.exists("/home/liveuser") else getpass.getuser()
    homedir = "/home/" + username

    system_info = {
        "username": username,
        "homedir": homedir,
        "phys_mem_raw": term("grep MemTotal /proc/meminfo"),
    }
    system_info["phys_mem_gb"] = round(
        int(re.sub("[^0-9]", "", system_info["phys_mem_raw"])) / 1048576
    )
    system_info["swappiness"] = min((200 // system_info["phys_mem_gb"]) * 2, 150)
    system_info["vfs_cache_pressure"] = int(
        max(min(system_info["swappiness"] * 1.25, 125), 32)
    )

    return system_info


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