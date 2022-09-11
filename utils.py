import os


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

def write_file(file_path,file_data):
     with open(file_path, "w") as file:
        file.write(file_data)



def replace_in_file(file_path, str, sub):
    """Replace string in file"""
    with open(file_path, "r") as file:
        filedata = file.read()

    filedata = filedata.replace(str, sub)

    with open(file_path, "w") as file:
        file.write(filedata)
