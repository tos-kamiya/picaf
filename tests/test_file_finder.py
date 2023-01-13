from typing import *

import unittest
import contextlib
import os
import sys
import tempfile
from pathlib import Path

from picaf.file_finder import pathlike_iter, existing_file_iter


@contextlib.contextmanager
def back_to_curdir():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


class PathlikeIterFuncTest(unittest.TestCase):
    def test_pathlike_iter_file_names(self):
        s = "  a.txt  b.txt  c.txt  d e.txt  fg.t x t  "
        #    012345678901234567890123456789012345678901
        #              1         2         3         4

        pos_fps = [(pos, fp) for pos, fp in pathlike_iter(s)]

        self.assertTrue(pos_fps[0][0] == 2 and pos_fps[0][1].startswith("a.txt"))
        self.assertTrue(pos_fps[1][0] == 9 and pos_fps[1][1].startswith("b.txt"))
        self.assertTrue(pos_fps[2][0] == 16 and pos_fps[2][1].startswith("c.txt"))
        self.assertTrue(pos_fps[3][0] == 23 and pos_fps[3][1].startswith("d e.txt"))
        self.assertTrue(pos_fps[4][0] == 25 and pos_fps[4][1].startswith("e.txt"))
        self.assertTrue(pos_fps[5][0] == 32 and pos_fps[5][1].startswith("fg.t x t"))
        self.assertTrue(pos_fps[6][0] == 37 and pos_fps[6][1].startswith("x t"))
        self.assertTrue(pos_fps[7][0] == 39 and pos_fps[7][1].startswith("t"))

    def test_pathlike_iter_file_paths(self):
        s = "  a/b.txt  c/d e.txt  f g/h.txt  i j/k l.txt  "
        #    0123456789012345678901234567890123456789013456
        #              1         2         3         4

        pos_fps = [(pos, fp) for pos, fp in pathlike_iter(s)]

        self.assertEqual(len(pos_fps), 8)
        self.assertTrue(pos_fps[0][0] == 2 and pos_fps[0][1].startswith("a/b.txt"))
        self.assertTrue(pos_fps[1][0] == 11 and pos_fps[1][1].startswith("c/d e.txt"))
        self.assertTrue(pos_fps[2][0] == 15 and pos_fps[2][1].startswith("e.txt"))
        self.assertTrue(pos_fps[3][0] == 22 and pos_fps[3][1].startswith("f g/h.txt"))
        self.assertTrue(pos_fps[4][0] == 24 and pos_fps[4][1].startswith("g/h.txt"))
        self.assertTrue(pos_fps[5][0] == 33 and pos_fps[5][1].startswith("i j/k l.txt"))
        self.assertTrue(pos_fps[6][0] == 35 and pos_fps[6][1].startswith("j/k l.txt"))
        self.assertTrue(pos_fps[7][0] == 39 and pos_fps[7][1].startswith("l.txt"))

    def test_pathlike_iter_relative_paths(self):
        s = "  ~/a.txt  ../b/c.txt  ./d e/f g.txt  /h/i.txt"
        #    0123456789012345678901234567890123456789012345
        #              1         2         3         4

        pos_fps = [(pos, fp) for pos, fp in pathlike_iter(s)]

        self.assertEqual(len(pos_fps), 6)
        self.assertTrue(pos_fps[0][0] == 2 and pos_fps[0][1].startswith("~/a.txt"))
        self.assertTrue(pos_fps[1][0] == 11 and pos_fps[1][1].startswith("../b/c.txt"))
        self.assertTrue(pos_fps[2][0] == 23 and pos_fps[2][1].startswith("./d e/f g.txt"))
        self.assertTrue(pos_fps[3][0] == 27 and pos_fps[3][1].startswith("e/f g.txt"))
        self.assertTrue(pos_fps[4][0] == 31 and pos_fps[4][1].startswith("g.txt"))
        self.assertTrue(pos_fps[5][0] == 38 and pos_fps[5][1].startswith("/h/i.txt"))


class ExistingFileIterFuncTest(unittest.TestCase):
    def test_existing_file_iter_simple(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with back_to_curdir():
                os.chdir(tempdir)

                Path('a.txt').touch()
                Path('d e.txt').touch()
                Path("x t").mkdir()

                s = "  a.txt  b.txt  c.txt  d e.txt  fg.t x t  "
                #    012345678901234567890123456789012345678901
                #              1         2         3         4

                ptfs = [(pos, typ, fp) for pos, typ, fp in existing_file_iter(s)]

                self.assertEqual(len(ptfs), 3)
                self.assertEqual(ptfs[0], (2, 'file', 'a.txt'))
                self.assertEqual(ptfs[1], (23, 'file', 'd e.txt'))
                self.assertEqual(ptfs[2], (37, 'directory', 'x t'))

    def test_existing_file_iter_relative_paths(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with back_to_curdir():
                os.chdir(tempdir)
                Path('hoge').mkdir()
                os.chdir('hoge')

                Path('a.txt').touch()
                Path('../b').mkdir()
                Path('../b/c.txt').touch()
                Path('d e').mkdir()
                Path('d e/f g.txt').touch()

                s = "    a.txt  ../b/c.txt  ./d e/f g.txt  /h/i.txt"
                #    0123456789012345678901234567890123456789012345
                #              1         2         3         4

                ptfs = [(pos, typ, fp) for pos, typ, fp in existing_file_iter(s)]

                self.assertEqual(len(ptfs), 3)
                self.assertEqual(ptfs[0], (4, 'file', 'a.txt'))
                self.assertEqual(ptfs[1], (11, 'file', '../b/c.txt'))
                self.assertEqual(ptfs[2], (23, 'file', './d e/f g.txt'))
