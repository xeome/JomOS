from dataclasses import replace
import re
import sys
import os
import utils
import logging
from rich.logging import RichHandler
from rich import print
from rich.panel import Panel

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

DRYRUN = 1

if DRYRUN:
    log.info("DRYRUN mode is on")

USERNAME = ("liveuser" if os.path.exists("/home/liveuser")
            else utils.term("whoami").replace("\n", ""))

HOMEDIR = "/home/" + USERNAME
PHYSMEMRAW = utils.term("grep MemTotal /proc/meminfo")

PHYSMEMGB = int(re.sub("[^0-9]", "", PHYSMEMRAW)) // 1048576
# get ram amount in kb and convert to gb with floor division

SWAPPINESS = min((200 // PHYSMEMGB) * 2, 150)
VFSCACHEPRESSURE = max(min(SWAPPINESS, 125), 32)

# TODO: add check for fstrim timers if ssd

COMMANDLIST = [
    "yay -S --noconfirm zram-generator irqbalance",
    "tar --use-compress-program=unzstd -xvf ./assets/themes.tar.zst",
    "mkdir ~/.themes",
    "cp -r ./themes/* ~/.themes",
    'xfconf-query -c xsettings -p /Net/ThemeName -s "Fluent-dark"',
    'xfconf-query -c xfwm4 -p /general/theme -s "Fluent-dark"',
    "sudo cp ./assets/wallpaper.png /usr/share/endeavouros/backgrounds/endeavouros-wallpaper.png",
    "sudo cp ./assets/gigachad_small.png /usr/share/endeavouros/EndeavourOS-icon.png",
    "bash ./chpanelcolor.sh 0 0 0 255",
]

FILELIST=[
    "/etc/sysctl.d/99-JomOS-settings.conf",
    "/etc/systemd/zram-generator.conf",
    "/etc/udev/rules.d/ioscheduler.rules",
    "/etc/makepkg.conf",
    "/etc/mkinitcpio.conf",
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

print(Panel.fit(ABOUT,title="JomOS alpha 0.1"))

confirmation = input(
    'Please type "Confirm" without quotes at the prompt to continue: \n'
)

if confirmation != "Confirm":
    log.warning("Warning not copied exactly.")
    sys.exit()

log.info(f"""USERNAME: "{USERNAME}"
RAM AMOUNT: {PHYSMEMGB}
CALCULATED SWAPPINESS: {SWAPPINESS}
CALCULATED VFS_CACHE_PRESSURE: {VFSCACHEPRESSURE}
""")


whiskermenupath = utils.term(
    "ls " + HOMEDIR + "/.config/xfce4/panel/whiskermenu-*.rc").replace("\n", "")

# Copy system makepkg.conf for necessary modifications
utils.term("cp /etc/makepkg.conf ./etc/makepkg.conf")


# Modify configuration files
try:
    utils.replaceinfile(
        "./etc/makepkg.conf",
        "#MAKEFLAGS=\"-j2\"",
        "MAKEFLAGS=\"-j$(nproc)\""
    )

    utils.replaceinfile("./etc/sysctl.d/99-JomOS-settings.conf",
                        "vm.swappiness = 30",
                        "vm.swappiness = " + str(SWAPPINESS)
                        )

    utils.replaceinfile(
        "./etc/sysctl.d/99-JomOS-settings.conf",
        "vm.vfs_cache_pressure = 50",
        "vm.vfs_cache_pressure = " + str(VFSCACHEPRESSURE),
    )

except Exception:
    # TODO: proper error handling
    log.error("Error when modifying configurations")

else:
    log.info("file /etc/sysctl.d/99-JomOS-settings.conf modified")
    log.info("file /etc/makepkg.conf modified")

if DRYRUN != 1:

    utils.installdir("./etc", "/", "-D -o root -g root -m 644")
    
    # TODO: not hardcode the file list
    for file in FILELIST:
        log.info("Modified file: " + file)
    
    for command in COMMANDLIST:
        utils.term(command)
        log.info("Command executed: " + command)

    utils.replaceinfile(
        str(whiskermenupath),
        "button-title=EndeavourOS",
        "button-title=JomOS",
    )
