import os
import re
import sys

HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

DRYRUN = 0


def exec(str):
    return os.popen(str).read()


def installdir(input, target, flags):
    exec(
        "find "
        + input
        + " -type f -exec sudo install "
        + flags
        + ' "{}" "'
        + target
        + '{}" \;'
    )


def replaceinfile(filepath, str, sub):
    # Read in the file
    with open(filepath, "r") as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(str, sub)

    # Write the file out again
    with open(filepath, "w") as file:
        file.write(filedata)


COMMANDLIST = [
    "yay -S --noconfirm zram-generator irqbalance timeshift-bin zsh vim",
    # "sudo install -o root -g root -m 644 ./etc/* /etc/",
    "tar --use-compress-program=unzstd -xvf themes.tar.zst",
    "mkdir ~/.themes",
    "cp -r ./themes/* ~/.themes",
    'xfconf-query -c xsettings -p /Net/ThemeName -s "Fluent-dark"',
    'xfconf-query -c xfwm4 -p /general/theme -s "Fluent-dark"',
    "sudo cp ./wallpaper.png /usr/share/endeavouros/backgrounds/endeavouros-wallpaper.png",
    "sudo cp ./gigachad_small.png /usr/share/endeavouros/EndeavourOS-icon.png",
    "bash ./chpanelcolor.sh 0 0 0 255",
]

text = """
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

print(text)

confirmation = input(
    'Please type "Confirm" without quotes at the prompt to continue: \n'
)

if confirmation != "Confirm":
    print("Warning not copied exactly.")
    sys.exit()
USERNAME = (
    "liveuser" if path.exists("/home/liveuser") else exec("whoami").replace("\n", "")
)

# USERNAME = "liveuser"  # exec("whoami").replace("\n", "")
HOMEDIR = "/home/" + USERNAME
PHYSMEMRAW = exec("grep MemTotal /proc/meminfo")

PHYSMEMGB = int(re.sub("[^0-9]", "", PHYSMEMRAW)) // 1048576
# get ram amount in kb and convert to gb with floor division

SWAPPINESS = min((200 // PHYSMEMGB) * 2, 150)
VFSCACHEPRESSURE = max(min(SWAPPINESS, 125), 32)

replaceinfile(
    "./etc/sysctl.d/99-swappiness.conf",
    "vm.swappiness=50",
    "vm.swappiness=" + str(SWAPPINESS),
)

replaceinfile(
    "./etc/sysctl.d/99-swappiness.conf",
    "vm.vfs_cache_pressure=50",
    "vm.vfs_cache_pressure=" + str(VFSCACHEPRESSURE),
)

# TODO: for loop running all commands from a list
if DRYRUN != 1:
    installdir("./etc", "/", "-D -o root -g root -m 644")
    for command in COMMANDLIST:
        exec(command)
    replaceinfile(
        HOMEDIR + "/.config/xfce4/panel/whiskermenu-1.rc",
        "button-title=EndeavourOS\ \ ",
        "button-title=JomOS\ \ ",
    )
