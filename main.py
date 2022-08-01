from dataclasses import replace
import re
import sys
import os
import utils

USERNAME = (
    "liveuser" if os.path.exists(
        "/home/liveuser") else utils.exec("whoami").replace("\n", "")
)

HOMEDIR = "/home/" + USERNAME
PHYSMEMRAW = utils.exec("grep MemTotal /proc/meminfo")

PHYSMEMGB = int(re.sub("[^0-9]", "", PHYSMEMRAW)) // 1048576
# get ram amount in kb and convert to gb with floor division

SWAPPINESS = min((200 // PHYSMEMGB) * 2, 150)
VFSCACHEPRESSURE = max(min(SWAPPINESS, 125), 32)

DRYRUN = 0

COMMANDLIST = [
    "yay -S --noconfirm zram-generator irqbalance timeshift-bin zsh vim",
    "tar --use-compress-program=unzstd -xvf ./assets/themes.tar.zst",
    "mkdir ~/.themes",
    "cp -r ./themes/* ~/.themes",
    'xfconf-query -c xsettings -p /Net/ThemeName -s "Fluent-dark"',
    'xfconf-query -c xfwm4 -p /general/theme -s "Fluent-dark"',
    "sudo cp ./assets/wallpaper.png /usr/share/endeavouros/backgrounds/endeavouros-wallpaper.png",
    "sudo cp ./assets/gigachad_small.png /usr/share/endeavouros/EndeavourOS-icon.png",
    "bash ./chpanelcolor.sh 0 0 0 255",
]

ABOUT = """
              ........              │|      JomOS alpha 0.1                                                     
         ..................         │|  JomOS is a meta Linux distribution which allows users to mix-and-match
      ........................      │|  well tested configurations and optimizations with little to no effort 
     ..............;ooc........     │|   
   ................;ddl..........   │|  JomOS integrates these configurations into one largely cohesive system.
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  .................;ddl...........  │|  
  ........:oo:.....cddc...........  │|  
   .......'lddl::coddl'..........   │|  
     .......,:clllc:,..........     │|  
       .......................      │|  
         ..................         │|  Continuing will:
              ........              │|  - Convert existing installation into JomOS
"""

print(ABOUT)

confirmation = input(
    'Please type "Confirm" without quotes at the prompt to continue: \n'
)

if confirmation != "Confirm":
    print("Warning not copied exactly.")
    sys.exit()


whiskermenupath = utils.exec(
    "ls " + HOMEDIR + "/.config/xfce4/panel/whiskermenu-*.rc").replace("\n", "")

# Copy system makepkg.conf for necessary modifications
exec("cp /etc/makepkg.conf ./etc/makepkg.conf")


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
    print("Error when modifying configurations")


if DRYRUN != 1:

    utils.installdir("./etc", "/", "-D -o root -g root -m 644")

    for command in COMMANDLIST:
        utils.exec(command)

    utils.replaceinfile(
        str(whiskermenupath),
        "button-title=EndeavourOS",
        "button-title=JomOS",
    )
