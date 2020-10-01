# -*- coding: utf8 -*-
'''
http://www.roguebasin.com/index.php?title=FOV_using_recursive_shadowcasting
缺点: 不对称，盲角

菱形墙:
http://www.adammil.net/blog/v125_Roguelike_Vision_Algorithms.html#diamondwalls
    1. 解决盲角(通过更宽容来实现), 但是会导致光通过门扩展太多（过于宽容导致可见tile变多）
        对于对角墙壁可移动的行为会更一致
改进版:
        http://www.adammil.net/blog/v125_Roguelike_Vision_Algorithms.html#mine
        1. 如果一个墙tile的两个相邻都不是墙，则将该角切成斜角。
        2. 如果光束与墙的形状相交，则墙tile可见；
        3. 如果光束与中心正方形（size最大为tile的1/2）相交，则空白tile可见。
        4. 与图形成切线不算相交，并且零宽度的扇形无法照亮
'''

from tgame import *

class Map(object):
    # Multipliers for transforming coordinates to other octants:
    mult = [
                [1,  0,  0, -1, -1,  0,  0,  1],
                [0,  1, -1,  0,  0, -1,  1,  0],
                [0,  1,  1,  0,  0, -1, -1,  0],
                [1,  0,  0,  1, -1,  0,  0, -1]
            ]
    def __init__(self, map):
        self.data = map
        self.width, self.height = len(map[0]), len(map)
        self.light = []
        for i in range(self.height):
            self.light.append([0] * self.width)
        self.flag = 0
    def square(self, x, y):
        return self.data[y][x]
    def blocked(self, x, y):
        return (x < 0 or y < 0
                or x >= self.width or y >= self.height
                or self.data[y][x] == "#")
    def lit(self, x, y):
        return self.light[y][x] == self.flag
    def set_lit(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.light[y][x] = self.flag
    def _cast_light(self, cx, cy, row, col, start, end, radius, xx, xy, yx, yy, id):
        "Recursive lightcasting function"
        if start <= end:
            return
        radius_squared = radius*radius
        for j in range(row, radius+1):
            dx, dy = -j-1, -j
            #dy = -j
            blocked = False
            start_col = -j
            while dx <= 0:
                dx += 1
            #for dx in range(-j, 1, 1):
                # Translate the dx, dy coordinates into map coordinates:
                X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
                # l_slope and r_slope store the slopes of the left and right
                # extremities of the square we're considering:
                # 原点到格子左上角，右下角的斜率
                l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
                #l_slope, r_slope = (dx-0.25)/(dy+0.25), (dx+0.25)/(dy-0.25)
                # 如此则格子的任何部分(而非中心)被包括在扫描范围就算到视野里
                if start <= r_slope:
                    continue
                elif end >= l_slope:
                    break
                else:
                    # Our light beam is touching this square; light it:
                    if dx*dx + dy*dy < radius_squared:
                        self.set_lit(X, Y)
                    if blocked:
                        # we're scanning a row of blocked squares:
                        if self.blocked(X, Y):
                            new_start = r_slope
                            continue
                        else:
                            blocked = False
                            start = new_start
                            start_col = dx
                    else:
                        if self.blocked(X, Y) and j < radius:
                            # This is a blocking square, start a child scan:
                            blocked = True
                            self._cast_light(cx, cy, j+1, start_col-1, start, l_slope,
                                             radius, xx, xy, yx, yy, id+1)
                            new_start = r_slope
            # Row is scanned; do next row unless last square was blocked:
            if blocked:
                break
    def do_fov(self, x, y, radius):
        "Calculate lit squares from the given location and radius"
        self.flag += 1
        for oct in range(8):
            self._cast_light(x, y, 1, -1, 1.0, 0.0, radius,
                             self.mult[0][oct], self.mult[1][oct],
                             self.mult[2][oct], self.mult[3][oct], 0)

FOV_RADIUS = 100

dungeon =  ["###########################################################",
            "#...........#.............................................#",
            "#...........#........#....................................#",
            "#.....................#...................................#",
            "#....####..............#..................................#",
            "#.......#.......................#####################.....#",
            "#.......#...........................................#.....#",
            "#.......#...........##..............................#.....#",
            "#####........#......##..........##################..#.....#",
            "#...#...........................#................#..#.....#",
            "#...#............#..............#................#..#.....#",
            "#...............................#..###############..#.....#",
            "#...............................#...................#.....#",
            "#...............................#...................#.....#",
            "#...............................#####################.....#",
            "#.........................................................#",
            "#.........................................................#",
            "###########################################################"]

if __name__ == '__main__':
    try:
        s = tgame_init()
        map = Map(dungeon)
        x, y = 36, 13
        while True:
            map.do_fov(x, y, FOV_RADIUS)
            tgame_display(s, map, x, y)
            k = s.getch()
            if k == 27:
                break
            elif k == 259: y -= 1
            elif k == 258: y += 1
            elif k == 260: x -= 1
            elif k == 261: x += 1
    finally:
        tgame_fini(s)
