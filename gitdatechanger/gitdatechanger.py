#!/usr/bin/env python3

from dateparser import parse
from datetime import datetime
from os import environ, chdir, getcwd
from pathlib import Path
from re import search
from subprocess import DEVNULL, check_output, run, CalledProcessError
from sys import argv

if (
    run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode
    != 0
):
    print("This script must be run from within a Git repository")
    exit(1)

if run(["git", "diff", "--quiet"], capture_output=True).returncode != 0:
    print(
        "Working directory is dirty: please commit changes or stash before runnning this script"
    )
    exit(1)

# Need to be at the root of the directory in case we start
# rebasing in a directory that doesn't exist in past commits
toplevel = check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
current_dir = getcwd()
if current_dir != toplevel:
    print(
        f"Warning: Running script from {toplevel}, if {current_dir} is created by any of the commits that are rebased you will need to change directories manually after running this script"
    )
    chdir(toplevel)

# Starts an "interactive" rebase that's not interactive at all:
# we use sed as an "editor" to edit every commit, but we'll
# only be changing the dates so it should be conflict free as long
# as you're not rebasing onto another branch: that's outside the scope
# of this script
def start_rebase(refspec, root=False):
    env = {"GIT_SEQUENCE_EDITOR": "sed -i -e 's/^pick /edit /g'"}
    print("Starting rebase at", refspec, "\n")
    run(
        ["git", "rebase", "-i", refspec, "--root" if root else "--"],
        env=env,
        text=True,
        stdout=DEVNULL,
        stderr=DEVNULL,
    )


# No conflicts expected or tolerated
def continue_rebase():
    print("Continuing rebase...\n")
    run(["git", "rebase", "--continue"], stdout=DEVNULL, stderr=DEVNULL)


def commit_at(date):
    new_date = datetime.strftime(date, "%c %z")

    env = {"GIT_COMMITTER_DATE": new_date, "HOME": environ["HOME"]}
    run(
        ["git", "commit", "--amend", "--no-edit", "--date", new_date],
        text=True,
        stdout=DEVNULL,
        stderr=DEVNULL,
        env=env,
    )


# Thanks to dateparser, the new date can be in
# almost any format:
# - 6. Jan 2019 19:14:26 (fully specified)
# - 20. Feb 2020 (just a day, will use the current time)
# - two months ago (relative to the current date and time)
# - 2 days and 15 minutes from now (in the future??)
# See more at https://github.com/scrapinghub/dateparser/#how-to-use
def ask_for_new_date(current_date):
    new_date = input("New date: ")
    if not new_date:
        print("Keeping current date...")
        return current_date

    parsed_date = parse(new_date)

    # User could specify a non-date
    if parsed_date is None:
        print(
            f"Unable to parse '{new_date}' as a date: will not change date for this commit"
        )
        return current_date

    # Use the same timezone unless user specified their own
    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.replace(tzinfo=current_date.tzinfo)

    return parsed_date


def num_available_commits():
    return len(check_output(["git", "log", "--oneline"]).splitlines())


def get_current_commit():
    commit_info = check_output(["git", "rebase", "--show-current-patch"], text=True)
    raw_date = search("Date:\s*(.*)", commit_info).group(1)
    parsed_date = datetime.strptime(raw_date, "%c %z")
    header = commit_info.splitlines()[4].strip()
    return parsed_date, header


if len(argv) < 2 or not argv[1].isdigit():
    scriptname = Path(argv[0]).name
    print(f"Usage: {scriptname} <steps back in history>")
    exit(1)

steps = int(argv[1])
num_commits = num_available_commits()
if steps > num_commits:
    print(f"Cannot go back {steps} steps, only {num_commits} commits in history")
    exit(1)

# If you're going all the way back to the first commit
# we need to use the '--root' flag
try:
    start_rebase(f"@~{steps}", root=(steps == num_commits))
    while steps >= 1:
        current_date, header = get_current_commit()
        print(f"{current_date} | {header}")
        new_date = ask_for_new_date(current_date)
        commit_at(new_date)
        print(f"{new_date} | {header}")
        continue_rebase()
        steps -= 1

    print("Finished rebasing successfully")
except CalledProcessError as cpe:
    cmd = " ".join(cpe.cmd)
    print(f"Failed to rebase: '{cmd}' returned {cpe.stdout}")
    run(["git", "rebase", "--quit"], stderr=DEVNULL, stdout=DEVNULL)
