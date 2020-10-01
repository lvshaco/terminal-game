# -*- coding: utf8 -*-
import curses

def tgame_init():
    def color_pairs():
        c = []
        for i in range(1, 16):
            curses.init_pair(i, i % 8, 0)
            if i < 8:
                c.append(curses.color_pair(i))
            else:
                c.append(curses.color_pair(i) | curses.A_BOLD)
        return c
    s = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    color_pairs()
    s.keypad(1)
    return s

def tgame_fini(s):
    s.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    print "Normal termination."

def tgame_display(s, _map, X, Y):
    dark, lit = curses.color_pair(8), curses.color_pair(7) | curses.A_BOLD
    for x in range(_map.width):
        for y in range(_map.height):
            if _map.lit(x, y):
                attr = lit
            else:
                attr = dark
            if x == X and y == Y:
                ch = '@'
                attr = lit
            else:
                ch = _map.square(x, y)
            s.addstr(y, x, ch, attr)
    s.refresh()
