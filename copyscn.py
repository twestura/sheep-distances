"""Called from an autohotkey script to copy and paste a scenario file."""


import os
import shutil


SCN_DIR = "PATH_TO_YOUR_DE_SCENARIO_FOLDER"  # noqa: E501
OUT_DIR = "D:/out"


def main():
    """Copies and pastes the files."""
    for file_name in os.listdir(SCN_DIR):
        scn_path = os.path.join(SCN_DIR, file_name)
        try:
            shutil.move(scn_path, OUT_DIR)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
