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


def write_file(file_path, file_data):
    with open(file_path, "w") as file:
        file.write(file_data)


def return_files(file_path):
    lst = list()
    for path, sub_dirs, files in os.walk(file_path):
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
