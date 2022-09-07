import os


def term(str):
    """Execute a terminal command"""
    return os.popen(str).read()


def installdir(input, target, flags):
    """Install a directory with necessary permissions"""
    term(
        "find "
        + input
        + " -type f -exec sudo install "
        + flags
        + ' "{}" "'
        + target
        + '{}" \;'
    )

def readfile(filepath):
    """Read file and return its contents"""
    with open(filepath, "r") as file:
        return file.read()

def readfilelines(filepath):
    """Read file and return its contents as lines"""
    with open(filepath, "r") as file:
        return [x.strip() for x in file.readlines()]



def replaceinfile(filepath, str, sub):
    """Replace string in file"""
    with open(filepath, "r") as file:
        filedata = file.read()

    filedata = filedata.replace(str, sub)

    with open(filepath, "w") as file:
        file.write(filedata)
