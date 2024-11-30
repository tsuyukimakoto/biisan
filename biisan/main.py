from datetime import datetime
import multiprocessing
import os
import sys

from biisan.constants import (
    ABOUT_TMPL,
    BIISAN_DATA_DIR,
    QUESTIONS,
    SETTINGS_TMPL,
)

import inquirer


def check_already_init(data_dir):
    if os.path.exists(data_dir):
        sys.exit("biisan data directory, {0} exists already.".format(BIISAN_DATA_DIR))


def initialize_structures(data_dir, answer):
    check_already_init(data_dir)
    os.mkdir(data_dir)
    os.mkdir(os.path.join(data_dir, "data"))
    os.mkdir(os.path.join(data_dir, "data", "blog"))
    os.mkdir(os.path.join(data_dir, "data", "templates"))
    os.mkdir(os.path.join(data_dir, "data", "extra"))
    os.mkdir(os.path.join(data_dir, "out"))
    with open(os.path.join(data_dir, "data", "biisan_local_settings.py"), "w") as f:
        f.write(
            SETTINGS_TMPL.format(
                multicore=multiprocessing.cpu_count(),
                **answer,
            ),
        )
    n = datetime.now()
    with open(os.path.join(data_dir, "data", "extra", "about.rst"), "w") as f:
        f.write(
            ABOUT_TMPL.format(
                year=n.year,
                month=n.month,
                day=n.day,
                hour=n.hour,
                minute=n.minute,
                **answer,
            ),
        )


def init():
    data_dir = os.path.join(os.getcwd(), BIISAN_DATA_DIR)
    check_already_init(data_dir)
    questions = [inquirer.Text(x["name"], message=x["message"]) for x in QUESTIONS]
    answer = inquirer.prompt(questions)
    initialize_structures(data_dir, answer)
    print("""
        Always set environment variable BIISAN_SETTINGS_MODULE to biisan_local_settings like bellow.

        $ export BIISAN_SETTINGS_MODULE=biisan_local_settings
        """)


if __name__ == "__main__":
    init()
