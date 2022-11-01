# picaf

`picaf` (Pick-up a file) is a tool to generate a clickable map of files.

Show the window that allows you to click filenames, from text containing file names.

A slightly similar tool is `python -m http.server`, which serves a web page including links to files in local directories.

For installation instructions, please refer to the [picaf website](https://github.com/tos-kamiya/picaf).

## Example of Use

`picaf` was originally designed for use with [dendro_text](https://github.com/tos-kamiya/dendro_text), which finds the similarity of text files and creates a dendrogram.

In this example, make the filenames clickable in the output of `dendro_text` so that you can investigate the content of each file with a text editor.

![](https://github.com/tos-kamiya/picaf/blob/main/images/fig1.png?raw=True)
