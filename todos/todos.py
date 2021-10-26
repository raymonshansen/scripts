#!/usr/bin/env python3

from subprocess import run, check_output
from re import search, IGNORECASE
from datetime import datetime
from itertools import groupby
from os import environ

try:
    import colorama

    colorama.init()
    BAD_COLOR = colorama.Fore.RED
    WARNING_COLOR = colorama.Fore.YELLOW
    OK_COLOR = colorama.Fore.GREEN
    RESET = colorama.Fore.RESET
except ImportError:
    BAD_COLOR = ""
    WARNING_COLOR = ""
    OK_COLOR = ""
    RESET = ""

MAX_AGE = int(environ.get("TODO_MAX_AGE") or 150)
OK_AGE = MAX_AGE // 2

if (
    run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode
    != 0
):
    print("This script must be run from within a Git repository")
    exit(1)

# Based on the following command:
# git grep -i "\(\/\/\|\#\)\s*TODO"
# -i for case insensitive match
# Finds all comments (either // or #) that start with the word "todo"
pattern = "\(\/\/\|\#\)\s*TODO:\?\s*\(.*\)"

# Helper functions for dating todos
def days_ago(timestamp):
    today = datetime.today()
    then = datetime.fromtimestamp(float(timestamp))
    return (today - then).days


def prettify(days):
    pluralized = "days" if days != 1 else "day"

    color = ""
    if days >= MAX_AGE:
        color = BAD_COLOR
    elif days >= OK_AGE:
        color = WARNING_COLOR
    else:
        color = OK_COLOR

    return f"{color}{days} {pluralized} old{RESET}"


def get_todos():
    raw_todos = run(
        ["git", "grep", "-i", "-n", pattern], capture_output=True, encoding="utf-8"
    )
    # No TODOs found!
    if raw_todos.returncode != 0:
        return

    for todo in raw_todos.stdout.splitlines():
        file, lineno, contents = todo.split(":", maxsplit=2)
        line = search("(//|#)\s*TODO:?\s*(.*)", contents, IGNORECASE).group(2)
        # blame for the specific line to get its age
        blame = check_output(
            ["git", "blame", "--date=raw", file, f"-L{lineno},{lineno}"],
            encoding="utf-8",
        )
        age = days_ago(search("[0-9]{10}", blame).group())

        yield (age, file, lineno, line)


todos = list(get_todos())
if not todos:
    print("No TODO comments found")
    exit(0)

todos_by_file = groupby(todos, lambda tup: tup[1])

total = 0
for filename, todos in todos_by_file:
    print(filename)
    for age, _, lineno, content in todos:
        pretty_age = prettify(age)
        print(f" {pretty_age} on line {lineno}: {content}")
        total += age

print(f"Total age of all TODOs is {total}")

# Exit with non-zero if we have too much debt
exit(1 if total >= MAX_AGE else 0)
