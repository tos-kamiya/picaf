from typing import List, Optional
import re
import shlex
import subprocess
import sys
import tkinter

import PySimpleGUI as sg
import pyautogui
from docopt import docopt

from .file_finder import existing_file_iter


def build_command_line(
    command: str, file_name: str, pattern: Optional[re.Pattern], max_capture_number: int
) -> List[str]:
    cmd = shlex.split(command)
    if max_capture_number < 0:
        cmd.append(file_name)
    elif pattern is None:
        if max_capture_number != 0:
            sys.exit("Error: no capture in pattern")
        for i, c in enumerate(cmd):
            cmd[i] = c.replace("{0}", file_name)
    else:
        m = pattern.match(file_name)
        if not m:
            assert False, "pattern match/unmatch inconsistent."
        if m.lastindex is None:
            if max_capture_number > 0:
                sys.exit("Error: not enough captures in pattern")
        elif m.lastindex < max_capture_number:
            sys.exit("Error: not enough captures in pattern")
        for i, c in enumerate(cmd):
            for j in range(max_capture_number + 1):
                c = c.replace("{%d}" % j, m.group(j))
            cmd[i] = c
    return cmd


class FileAction:
    def __init__(
        self,
        file_name: str,
        command: Optional[str],
        pattern: Optional[re.Pattern],
        max_capture_number: int,
        dry_run: bool,
    ):
        self.file_name = file_name
        self.dry_run = dry_run
        self.cmd = build_command_line(command, file_name, pattern, max_capture_number) if command is not None else None

    def __call__(self):
        if self.cmd is None:
            print("%s" % self.file_name)
            return

        if self.dry_run:
            print(shlex.join(self.cmd))
            return

        exit_code = subprocess.call(self.cmd)
        if exit_code != 0:
            sys.exit(exit_code)


__doc__ = """Make a clickable map of files from a text file.

Usage:
  picaf [options] [<textfile>]

Options:
  -c COMMAND, --command=COMMAND     Command line for the clicked file. `{0}` is a place holder to put a file name.
  -p PAT, --pattern=PAT     Pattern to filter / capture files.
  -n, --dry-run             Print commands without running.
  --font=NAMESIZE           Specify font name and size, e.g. `"Noto Sans,12"`
  --font-list               Print the fonts installed.
  --theme=THEME             Specify theme [default: LightGray].
  --theme-preview           Show theme previewer.
"""


def main():
    args = docopt(__doc__)
    font: Optional[str] = args["--font"]
    command: Optional[str] = args["--command"]
    textfile: Optional[str] = args["<textfile>"]
    dry_run: bool = args["--dry-run"]
    pattern_str: Optional[str] = args["--pattern"]
    theme: str = args["--theme"]

    list_fonts: bool = args["--font-list"]
    preview_themes: str = args["--theme-preview"]

    pattern = re.compile(pattern_str) if pattern_str is not None else None

    if list_fonts:
        fonts = list(sorted(set(sg.Text.fonts_installed_list())))
        print("\n".join(fonts))
        return
    elif preview_themes:
        sg.theme_previewer()
        return

    root = tkinter.Tk()
    fixed_font = tkinter.font.nametofont('TkFixedFont').actual()
    font_spec = fixed_font['family'], fixed_font['size']
    root.withdraw()

    sg.theme(theme)

    if font:
        ns = font.split(",")
        if len(ns) != 2:
            sys.exit("Error: --font option requires FONTNAME:FONTSIZE as an argument")
        try:
            s = int(ns[1])
        except ValueError:
            sys.exit("Error: font size must be integer")
        font_spec = ns[0], s

    sg.set_options(font=font_spec)

    max_capture_number = -1
    if command is not None:
        for m in re.finditer(r"{(\d+)}", command):
            n = int(m.group(1))
            if n < 0:
                sys.exit("Error: capture number should be zero or positive: `{%s}`" % m.group(1))
            max_capture_number = max(max_capture_number, n)

    def gen_action(file_name):
        return FileAction(file_name, command, pattern, max_capture_number, dry_run)

    if textfile is not None:
        with open(textfile, "r") as inp:
            lines = inp.readlines()
    else:
        lines = sys.stdin.readlines()
    lines = [L.rstrip() for L in lines]

    rows = []

    for L in lines:
        row = []
        last_p = 0
        for p, k, s in existing_file_iter(L):
            if k == "file" and (pattern is None or pattern.match(s)):
                if last_p < p:
                    row.append(sg.Text(L[last_p:p]))
                row.append(sg.Button(s, pad=(0, 1), key=gen_action(s)))
                last_p = p + len(s)
            else:
                if last_p < p + len(s):
                    row.append(sg.Text(L[last_p : p + len(s)]))
                last_p = p + len(s)
        else:
            if last_p < len(L):
                row.append(sg.Text(L[last_p:]))
        rows.append(row)

    mouse_position = pyautogui.position()
    layout = [[sg.Column(rows, scrollable=True, expand_x=True, expand_y=True)]]
    window = sg.Window("picaf", layout, margins=(0, 0), location=mouse_position, resizable=True)

    while True:
        event, values = window.read()
        if event is None:
            break
        if callable(event):
            event()

    window.close()


if __name__ == "__main__":
    main()
