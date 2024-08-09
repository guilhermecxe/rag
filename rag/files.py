import os

from .settings import SETTINGS


if not os.path.exists(SETTINGS.get('CONTENTS_PATH')):
    os.mkdir(SETTINGS.get('CONTENTS_PATH'))

def get_folders() -> list[str]:
    return os.listdir(SETTINGS.get('CONTENTS_PATH'))

def get_files(folder, type_=None, with_path=False) -> list[str] | list[tuple[str, str]]:
    folder_path = os.path.join(SETTINGS.get('CONTENTS_PATH'), folder)

    if with_path:
        return [(file, os.path.join(folder_path, file)) for file in os.listdir(folder_path)]
    else:
        return [file for file in os.listdir(folder_path)]

def get_all_files(as_tree=False):
    folders = get_folders()
    if as_tree:
        files = {}
        for folder in folders:
            files[folder] = get_files(folder)
    else:
        files = []
        for folder in folders:
            for _, file_path in get_files(folder, with_path=True):
                files.append(file_path)
    return files

def tree_to_list(tree:dict) -> list:
    file_paths = []
    for folder, files in tree.items():
        for file in files:
            path = os.path.join(SETTINGS.get('CONTENTS_PATH'), folder, file)
            file_paths.append(path)
    return file_paths
