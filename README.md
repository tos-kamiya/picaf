# picaf

Show the window that allows you to click filenames, which are picked up by scanning input text file.

A slightly similar tool is `python -m http.server`, which serves a web page including links to files in local directories.

## Installation

```sh
pip install picaf
```

If you get a ModuleNotFoundError when you run the picaf,

```sh
$ picaf -h
....
ModuleNotFoundError: No module named 'docopt'
```

Install docopt-ng additionally.

```sh
pip install docopt-ng
```

## Usage

```sh
picaf [options] [<textfile>]
```

Launch a GUI application that displays text in the argument files, after convert each filename written in text into a clickable button.

By default, each time a button is pressed, print the filename. With the option `-c`, you can execute the specified command for the filename.

### Options

```
-c COMMAND, --command=COMMAND     Command line for the clicked file. `{0}` is a place holder to put a file name.
-p PAT, --pattern PAT     Pattern to filter / capture files.
-n, --dry-run             Print commands without running.
--font=NAMESIZE           Specify font name and size, e.g. `"Noto Sans,12"`
--font-list               Print the fonts installed.
--theme=THEME             Specify theme [default: LightGray].
--theme-preview           Show theme previewer.
```

### Example of Use

picaf was originally designed for use with [dendro_text](https://github.com/tos-kamiya/dendro_text), which finds the similarity of text files and creates a dendrogram.

In this example, make the filenames clickable in the output of `dendro_text` so that you can investigate the content of each file with a text editor.

![](./images/fig1.png)
