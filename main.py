WScreen = 1280
HScreen = 720
WMaze = 20
HMaze = 20
Difficulty = 100  # >=0
sizekoef = 30
generation = "WS"  # "WS" or "DFS"
search = "A*"  # "G" or "A*"
showpath = True
ghostnumber = 2 # default ghost number in level 1
walldensity = 0.3

import pygame
import random
import math
import queue
import sys
import heapq

sys.setrecursionlimit(WMaze * HMaze + 10000)
top = (HScreen - HMaze * sizekoef) // 2
left = (WScreen - WMaze * sizekoef) // 2


class Cell:
    Walls = [0, 0, 0, 0]
    posx = 0
    posy = 0
    Cheese = 0


class Object:
    start = -1
    posx = 0
    posy = 0
    x = 0
    y = 0
    xprev = 0
    yprev = 0
    typ = "Pacman"
    direct = 0
    color = (0, 0, 255)
    number = -1


class Collision:
    happened = False


def graph():
    screen.fill((0, 0, 0))
    for row in Cells:
        for c in row:
            if c.Walls[0] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx + sizekoef, top + c.posy),
                                 (left + c.posx + sizekoef, top + c.posy + sizekoef))
            if c.Walls[1] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx, top + c.posy),
                                 (left + c.posx + sizekoef, top + c.posy))
            if c.Walls[2] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx, top + c.posy),
                                 (left + c.posx, top + c.posy + sizekoef))
            if c.Walls[3] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx, top + c.posy + sizekoef),
                                 (left + c.posx + sizekoef, top + c.posy + sizekoef))
    if showpath:
        m = 1
        for i in range(WMaze):
            for j in range(HMaze):
                Entered[j][i][0] = Entered[j][i][0] + 1
                m = max(m, Entered[j][i][0])
        for i in range(WMaze):
            for j in range(HMaze):
                color = (255 * Entered[j][i][0] // m, 255 * Entered[j][i][0] // m, 255 * Entered[j][i][0] // m)
                pygame.draw.circle(screen, color,
                                   (left + sizekoef * i + sizekoef // 2, top + sizekoef * j + sizekoef // 2),
                                   sizekoef // 3)
        for c in path:
            pygame.draw.circle(screen, (255, 0, 0),
                               (left + sizekoef * c[0] + sizekoef // 2, top + sizekoef * c[1] + sizekoef // 2),
                               sizekoef // 3)
    for obj in objects:
        pygame.draw.circle(screen, obj.color, (
            left + int(sizekoef * obj.posx) + sizekoef // 2, top + int(sizekoef * obj.posy) + sizekoef // 2),
                           sizekoef // 2)
        if obj.typ == "Ghost" and abs(obj.posx - player.posx) + abs(obj.posy - player.posy) < 0.2:
            collision.happened = True
    pygame.draw.circle(screen, (255, 255, 0),
                       (left + sizekoef * coin[0] + sizekoef // 2, top + sizekoef * coin[1] + sizekoef // 2),
                       sizekoef // 4)


def CheckConnection():
    used = []
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            row.append(False)
        used.append(row)
    q = []
    q.append((0, 0))
    used[0][0] = True
    while (len(q) > 0):
        pos = q[0]
        x = pos[0]
        y = pos[1]
        if Cells[x][y].Walls[0] == 0 and used[x][y + 1] == False:
            q.append((x, y + 1))
            used[x][y + 1] = True
        if Cells[x][y].Walls[1] == 0 and used[x - 1][y] == False:
            q.append((x - 1, y))
            used[x - 1][y] = True
        if Cells[x][y].Walls[2] == 0 and used[x][y - 1] == False:
            q.append((x, y - 1))
            used[x][y - 1] = True
        if Cells[x][y].Walls[3] == 0 and used[x + 1][y] == False:
            q.append((x + 1, y))
            used[x + 1][y] = True
        q.pop(0)
    ans = True
    for i in used:
        for j in i:
            ans = ans and j
    return ans


def dfs(i, j, direc):
    used[j][i] = True
    possibles = [0, 1, 2, 3]
    random.shuffle(possibles)
    for decision in possibles:
        if decision == 2:
            if i > 0 and not (used[j][i - 1]):
                dfs(i - 1, j, 0)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[2] = 1
        if decision == 0:
            if i < WMaze - 1 and not (used[j][i + 1]):
                dfs(i + 1, j, 2)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[0] = 1
        if decision == 1:
            if j > 0 and not (used[j - 1][i]):
                dfs(i, j - 1, 3)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[1] = 1
        if decision == 3:
            if j < HMaze - 1 and not (used[j + 1][i]):
                dfs(i, j + 1, 1)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[3] = 1
    if direc >= 0:
        Cells[j][i].Walls[direc] = 0


def prob():
    return math.exp(-Difficulty / 3)


def prior(x, y, x1, y1, x2, y2):
    if search == "G":
        return abs(x - x2) + abs(y - y2)
    if search == "A*":
        return abs(x - x2) + abs(y - y2) + (Entered[y][x][0] * 2) // 4


def findPath(x1, y1, x2, y2, Entered):
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            row.append([-1, -1, -1])
        Entered.append(row)
    q = []
    heapq.heappush(q, (0, x1, y1, -1, -1))
    while len(q) > 0:
        pos = heapq.heappop(q)
        x = pos[1]
        y = pos[2]
        xprev = pos[3]
        yprev = pos[4]
        if xprev != -1:
            Entered[y][x] = [Entered[y][x][0], xprev, yprev]
        else:
            Entered[y][x] = [0, -1, -1]
        if x == x2 and y == y2:
            break
        if x > 0 and Cells[y][x].Walls[2] == 0 and Entered[y][x - 1][0] == -1:
            Entered[y][x - 1][0] = Entered[y][x][0] + 1
            heapq.heappush(q, (prior(x - 1, y, x1, y1, x2, y2), x - 1, y, x, y))
        if x < WMaze - 1 and Cells[y][x].Walls[0] == 0 and Entered[y][x + 1][0] == -1:
            Entered[y][x + 1][0] = Entered[y][x][0] + 1
            heapq.heappush(q, (prior(x + 1, y, x1, y1, x2, y2), x + 1, y, x, y))
        if y > 0 and Cells[y][x].Walls[1] == 0 and Entered[y - 1][x][0] == -1:
            Entered[y - 1][x][0] = Entered[y][x][0] + 1
            heapq.heappush(q, (prior(x, y - 1, x1, y1, x2, y2), x, y - 1, x, y))
        if y < HMaze - 1 and Cells[y][x].Walls[3] == 0 and Entered[y + 1][x][0] == -1:
            Entered[y + 1][x][0] = Entered[y][x][0] + 1
            heapq.heappush(q, (prior(x, y + 1, x1, y1, x2, y2), x, y + 1, x, y))
    xans = x2
    yans = y2
    ans = []
    while xans != x1 or yans != y1:
        ans.insert(0, (xans, yans))
        (xans, yans) = (Entered[yans][xans][1], Entered[yans][xans][2])
    return ans


score = 0
collision = Collision()
collision.happened = False
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((WScreen, HScreen))
pygame.display.set_caption("PacMan")
screen.fill((0, 0, 10))
pygame.display.flip()
Cells = []
for i in range(HMaze):
    row = []
    for j in range(WMaze):
        c = Cell()
        c.Walls = [0, 0, 0, 0]
        c.posx = j * sizekoef
        c.posy = i * sizekoef
        row.append(c)
    Cells.append(row)
for i in range(HMaze):
    Cells[i][0].Walls[2] = 1
    Cells[i][WMaze - 1].Walls[0] = 1
for j in range(WMaze):
    Cells[0][j].Walls[1] = 1
    Cells[HMaze - 1][j].Walls[3] = 1
if generation == "WS":
    possiblewalls = []
    for i in range(WMaze):
        for j in range(HMaze):
            for k in range(2):
                if random.uniform(0, 1) <= walldensity:
                    possiblewalls.append((i, j, k))
    random.shuffle(possiblewalls)
    for w in possiblewalls:
        i = w[0]
        j = w[1]
        t = w[2]
        if t == 0 and i < WMaze - 1:
            if sum(Cells[j][i].Walls) < 2 and sum(Cells[j][i + 1].Walls) < 2:
                Cells[j][i].Walls[0] = 1
                Cells[j][i + 1].Walls[2] = 1
                if not (CheckConnection()):
                    Cells[j][i].Walls[0] = 0
                    Cells[j][i + 1].Walls[2] = 0
        if t == 1 and j > 0:
            if sum(Cells[j][i].Walls) < 2 and sum(Cells[j - 1][i].Walls) < 2:
                Cells[j][i].Walls[1] = 1
                Cells[j - 1][i].Walls[3] = 1
                if not (CheckConnection()):
                    Cells[j][i].Walls[1] = 0
                    Cells[j - 1][i].Walls[3] = 0
        if t == 2 and i > 0:
            if sum(Cells[j][i].Walls) < 2 and sum(Cells[j][i - 1].Walls) < 2:
                Cells[j][i].Walls[2] = 1
                Cells[j][i - 1].Walls[0] = 1
                if not (CheckConnection()):
                    Cells[j][i].Walls[2] = 0
                    Cells[j][i - 1].Walls[0] = 0
        if t == 3 and j < HMaze - 1:
            if sum(Cells[j][i].Walls) < 2 and sum(Cells[j + 1][i].Walls) < 2:
                Cells[j][i].Walls[3] = 1
                Cells[j + 1][i].Walls[1] = 1
                if not (CheckConnection()):
                    Cells[j][i].Walls[3] = 0
                    Cells[j + 1][i].Walls[1] = 0
if generation == "DFS":
    used = []
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            row.append(False)
        used.append(row)
    dfs(0, 0, -1)
Entered = []
pacman = (random.randint(0, WMaze - 1), random.randint(0, HMaze - 1))
coin = (random.randint(0, WMaze - 1), random.randint(0, HMaze - 1))
while abs(pacman[0] - coin[0]) + abs(pacman[1] - coin[1]) <= (WMaze // 4):
    coin = (random.randint(0, WMaze - 1), random.randint(0, HMaze - 1))
path = findPath(pacman[0], pacman[1], coin[0], coin[1], Entered)
running = True
arrow = ""
objects = []
player = Object()
player.x = pacman[0]
player.y = pacman[1]
player.xprev = player.posx
player.yprev = player.posy
player.typ = "Pacman"
player.color = (255, 255, 0)
objects.append(player)
gn = 0
first = None
for i in range(ghostnumber):
    gh = Object()
    gh.x = random.randint(0, WMaze - 1)
    gh.y = random.randint(0, HMaze - 1)
    while abs(pacman[0] - gh.x) + abs(pacman[1] - gh.y) <= (WMaze // 4):
        gh.x = random.randint(0, WMaze - 1)
        gh.y = random.randint(0, HMaze - 1)
    gh.xprev = gh.x
    gh.yprev = gh.y
    gh.typ = "Ghost"
    gh.color = (random.randint(0, 255), random.randint(0, 255), 255)
    gh.number = gn
    if gn == 0:
        first = gh
    gn += 1
    objects.append(gh)

# Global variables for levels and difficulty adjustments
current_level = 1
ghost_increment = 2  # Increase ghost number by 2 each level
difficulty_increment = 20  # Increase difficulty by 20 each level


# Function to reset the game for the next level
def next_level():
    global ghostnumber, Difficulty, player, objects, pacman, coin, path, current_level

    current_level += 1
    ghostnumber += ghost_increment  # Increase ghost number
    Difficulty += difficulty_increment  # Increase difficulty

    # Regenerate maze
    Cells.clear()
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            c = Cell()
            c.Walls = [0, 0, 0, 0]
            c.posx = j * sizekoef
            c.posy = i * sizekoef
            row.append(c)
        Cells.append(row)
    for i in range(HMaze):
        Cells[i][0].Walls[2] = 1
        Cells[i][WMaze - 1].Walls[0] = 1
    for j in range(WMaze):
        Cells[0][j].Walls[1] = 1
        Cells[HMaze - 1][j].Walls[3] = 1
    if generation == "WS":
        possiblewalls = []
        for i in range(WMaze):
            for j in range(HMaze):
                for k in range(2):
                    if random.uniform(0, 1) <= walldensity:
                        possiblewalls.append((i, j, k))
        random.shuffle(possiblewalls)
        for w in possiblewalls:
            i = w[0]
            j = w[1]
            t = w[2]
            if t == 0 and i < WMaze - 1:
                if sum(Cells[j][i].Walls) < 2 and sum(Cells[j][i + 1].Walls) < 2:
                    Cells[j][i].Walls[0] = 1
                    Cells[j][i + 1].Walls[2] = 1
                    if not CheckConnection():
                        Cells[j][i].Walls[0] = 0
                        Cells[j][i + 1].Walls[2] = 0
            if t == 1 and j > 0:
                if sum(Cells[j][i].Walls) < 2 and sum(Cells[j - 1][i].Walls) < 2:
                    Cells[j][i].Walls[1] = 1
                    Cells[j - 1][i].Walls[3] = 1
                    if not CheckConnection():
                        Cells[j][i].Walls[1] = 0
                        Cells[j - 1][i].Walls[3] = 0
            if t == 2 and i > 0:
                if sum(Cells[j][i].Walls) < 2 and sum(Cells[j][i - 1].Walls) < 2:
                    Cells[j][i].Walls[2] = 1
                    Cells[j][i - 1].Walls[0] = 1
                    if not CheckConnection():
                        Cells[j][i].Walls[2] = 0
                        Cells[j][i - 1].Walls[0] = 0
            if t == 3 and j < HMaze - 1:
                if sum(Cells[j][i].Walls) < 2 and sum(Cells[j + 1][i].Walls) < 2:
                    Cells[j][i].Walls[3] = 1
                    Cells[j + 1][i].Walls[1] = 1
                    if not CheckConnection():
                        Cells[j][i].Walls[3] = 0
                        Cells[j + 1][i].Walls[1] = 0
    if generation == "DFS":
        used = []
        for i in range(HMaze):
            row = []
            for j in range(WMaze):
                row.append(False)
            used.append(row)
        dfs(0, 0, -1)

    # Clear objects and set up new game state
    objects = []

    # Reset Pacman's position
    pacman = (random.randint(0, WMaze - 1), random.randint(0, HMaze - 1))
    player = Object()
    player.x = pacman[0]
    player.y = pacman[1]
    player.xprev = player.posx
    player.yprev = player.posy
    player.typ = "Pacman"
    player.color = (255, 255, 0)
    objects.append(player)

    # Reset coin position
    coin = (random.randint(0, WMaze - 1), random.randint(0, HMaze - 1))
    while abs(pacman[0] - coin[0]) + abs(pacman[1] - coin[1]) <= (WMaze // 4):
        coin = (random.randint(0, WMaze - 1), random.randint(0, HMaze - 1))

    # Reset ghosts with increased number
    for i in range(ghostnumber):
        gh = Object()
        gh.x = random.randint(0, WMaze - 1)
        gh.y = random.randint(0, HMaze - 1)
        while abs(pacman[0] - gh.x) + abs(pacman[1] - gh.y) <= (WMaze // 4):
            gh.x = random.randint(0, WMaze - 1)
            gh.y = random.randint(0, HMaze - 1)
        gh.xprev = gh.x
        gh.yprev = gh.y
        gh.typ = "Ghost"
        gh.color = (random.randint(0, 255), random.randint(0, 255), 255)
        gh.number = i
        objects.append(gh)

    # Reset the path for the new level
    Entered = []
    path = findPath(pacman[0], pacman[1], coin[0], coin[1], Entered)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                arrow = "Down"
            if event.key == pygame.K_UP:
                arrow = "Up"
            if event.key == pygame.K_LEFT:
                arrow = "Left"
            if event.key == pygame.K_RIGHT:
                arrow = "Right"
    for obj in objects:
        if obj.typ == "Ghost":
            if obj.start == -1 or pygame.time.get_ticks() - obj.start >= 600:
                if random.uniform(0, 1) < prob():
                    obj.start = pygame.time.get_ticks()
                    obj.xprev = obj.x
                    obj.yprev = obj.y
                    d = obj.direct
                    if Cells[obj.y][obj.x].Walls[d] == 1:
                        r = random.randint(0, 1)
                        if r == 0:
                            d = d + 1
                            d = d % 4
                            if Cells[obj.y][obj.x].Walls[d] == 1:
                                d = d + 2
                                d = d % 4
                                if Cells[obj.y][obj.x].Walls[d] == 1:
                                    d = d + 3
                                    d = d % 4
                        if r == 1:
                            d = d + 3
                            d = d % 4
                            if Cells[obj.y][obj.x].Walls[d] == 1:
                                d = d + 2
                                d = d % 4
                                if Cells[obj.y][obj.x].Walls[d] == 1:
                                    d = d + 1
                                    d = d % 4
                    obj.direct = d
                    if d == 0:
                        obj.x = obj.x + 1
                    elif d == 1:
                        obj.y = obj.y - 1
                    elif d == 2:
                        obj.x = obj.x - 1
                    elif d == 3:
                        obj.y = obj.y + 1
                else:
                    obj.start = pygame.time.get_ticks()
                    obj.xprev = obj.x
                    obj.yprev = obj.y
                    temp = []
                    temppath = findPath(obj.x, obj.y, player.x, player.y, temp)
                    temp = []
                    playerpath = findPath(player.x, player.y, coin[0], coin[1], temp)
                    if len(temppath) > 0:
                        if obj.number == 0:
                            obj.x = temppath[0][0]
                            obj.y = temppath[0][1]
                        elif obj.number == 1:
                            if abs(obj.x - player.x) + abs(obj.y - player.y) > 3:
                                targetx = player.x - (player.y - first.y)
                                targety = player.y + (player.x - first.x)
                            else:
                                targetx = player.x
                                targety = player.y
                            if targetx < 0:
                                targetx = 0
                            if targety < 0:
                                targety = 0
                            if targety >= HMaze:
                                targety = HMaze - 1
                            if targetx >= WMaze:
                                targetx = WMaze - 1
                            temp = []
                            temppath = findPath(obj.x, obj.y, targetx, targety, temp)
                            if len(temppath) > 0:
                                obj.x = temppath[0][0]
                                obj.y = temppath[0][1]
                        elif obj.number == 2:
                            if abs(obj.x - player.x) + abs(obj.y - player.y) > 3:
                                targetx = player.x + (player.y - first.y)
                                targety = player.y - (player.x - first.x)
                            else:
                                targetx = player.x
                                targety = player.y
                            if targetx < 0:
                                targetx = 0
                            if targety < 0:
                                targety = 0
                            if targety >= HMaze:
                                targety = HMaze - 1
                            if targetx >= WMaze:
                                targetx = WMaze - 1
                            temp = []
                            temppath = findPath(obj.x, obj.y, targetx, targety, temp)
                            if (len(temppath) > 0):
                                obj.x = temppath[0][0]
                                obj.y = temppath[0][1]
                        elif (len(temppath) <= 4):
                            obj.x = temppath[0][0]
                            obj.y = temppath[0][1]
                        else:
                            point = len(playerpath) // (ghostnumber - 3)
                            point *= (obj.number - 2)
                            point = len(playerpath) - point
                            targetx = 0
                            targety = 0
                            if (point < len(playerpath) and point >= 0):
                                targetx = playerpath[point][0]
                                targety = playerpath[point][1]
                            else:
                                targetx = player.x
                                targety = player.y
                            targetx += random.randint(0, 2) - 1
                            targety += random.randint(0, 2) - 1
                            if (targetx < 0):
                                targetx = 0
                            if (targety < 0):
                                targety = 0
                            if (targety >= HMaze):
                                targety = HMaze - 1
                            if (targetx >= WMaze):
                                targetx = WMaze - 1
                            temp = []
                            temppath = findPath(obj.x, obj.y, targetx, targety, temp)
                            if (len(temppath) > 0):
                                obj.x = temppath[0][0]
                                obj.y = temppath[0][1]

            obj.posx = (((max(0, 600 - pygame.time.get_ticks() + obj.start)) / 600) * obj.xprev + (
                    ((min(600, pygame.time.get_ticks() - obj.start)) / 600) * obj.x))
            obj.posy = (((max(0, 600 - pygame.time.get_ticks() + obj.start)) / 600) * obj.yprev + (
                    ((min(600, pygame.time.get_ticks() - obj.start)) / 600) * obj.y))
        if obj.typ == "Pacman":
            if obj.start == -1 or pygame.time.get_ticks() - obj.start >= 400:
                if obj.x == coin[0] and obj.y == coin[1]:
                    score += 1
                    print("Score: " + str(score))
                    next_level()  # Move to the next level when coin is collected
                obj.start = pygame.time.get_ticks()
                obj.xprev = obj.x
                obj.yprev = obj.y
                if arrow == "Right" and Cells[obj.y][obj.x].Walls[0] == 0:
                    obj.x = obj.x + 1
                    obj.direct = 0
                elif arrow == "Up" and Cells[obj.y][obj.x].Walls[1] == 0:
                    obj.y = obj.y - 1
                    obj.direct = 1
                elif arrow == "Left" and Cells[obj.y][obj.x].Walls[2] == 0:
                    obj.x = obj.x - 1
                    obj.direct = 2
                elif arrow == "Down" and Cells[obj.y][obj.x].Walls[3] == 0:
                    obj.y = obj.y + 1
                    obj.direct = 3
                elif arrow != "" and Cells[obj.y][obj.x].Walls[obj.direct] == 0:
                    if obj.direct == 0:
                        obj.x = obj.x + 1
                        arrow = "Right"
                    if obj.direct == 1:
                        obj.y = obj.y - 1
                        arrow = "Up"
                    if obj.direct == 2:
                        obj.x = obj.x - 1
                        arrow = "Left"
                    if obj.direct == 3:
                        obj.y = obj.y + 1
                        arrow = "Down"
            else:
                if ((arrow == "Left" and obj.direct == 0) or (arrow == "Up" and obj.direct == 3) or (
                        arrow == "Down" and obj.direct == 1)):
                    obj.xprev, obj.x = obj.x, obj.xprev
                    obj.yprev, obj.y = obj.y, obj.yprev
                    obj.start = pygame.time.get_ticks() - (400 - pygame.time.get_ticks() + obj.start)
                    obj.direct += 2
                    obj.direct %= 4

            Entered = []
            path = findPath(obj.x, obj.y, coin[0], coin[1], Entered)
            obj.posx = (((max(0, 400 - pygame.time.get_ticks() + obj.start)) / 400) * obj.xprev + (
                    ((min(400, pygame.time.get_ticks() - obj.start)) / 400) * obj.x))
            obj.posy = (((max(0, 400 - pygame.time.get_ticks() + obj.start)) / 400) * obj.yprev + (
                    ((min(400, pygame.time.get_ticks() - obj.start)) / 400) * obj.y))

            # Check for collisions with ghosts
    for obj in objects:
        if obj.typ == "Ghost" and obj.x == player.x and obj.y == player.y:
            print("GAME OVER")
            running = False
            break

    graph()
    pygame.display.flip()
