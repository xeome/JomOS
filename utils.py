import os


def term(str):
    """execute a terminal command"""
    return os.popen(str).read()


def installdir(input, target, flags):
    """install a directory with necessary permissions"""
    term(
        "find "
        + input
        + " -type f -exec sudo install "
        + flags
        + ' "{}" "'
        + target
        + '{}" \;'
    )


def replaceinfile(filepath, str, sub):
    """replace string in file"""
    with open(filepath, "r") as file:
        filedata = file.read()

    filedata = filedata.replace(str, sub)

    with open(filepath, "w") as file:
        file.write(filedata)
