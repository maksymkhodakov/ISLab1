# Константи для розміру екрану та параметрів лабіринту
WScreen = 1280  # Ширина екрану
HScreen = 720  # Висота екрану
WMaze = 20  # Ширина лабіринту (кількість клітин)
HMaze = 20  # Висота лабіринту (кількість клітин)
Difficulty = 0  # Рівень складності (>=0)
sizekoef = 30  # Коефіцієнт розміру кожної клітинки
generation = "WS"  # Метод генерації лабіринту: "WS" або "DFS"
search = "BFS"  # Алгоритм пошуку шляху: "G" (жадібний) або "A*" або BFS
showpath = True  # Відображати шлях чи ні
ghostnumber = 4  # Кількість привидів на першому рівні
walldensity = 0.3  # Щільність стін у лабіринті

# Імпорт бібліотек для графіки та алгоритмів
import pygame
import random
import math
import queue
import sys
import heapq

# Встановлюємо обмеження на кількість рекурсивних викликів
sys.setrecursionlimit(WMaze * HMaze + 10000)

# Визначаємо початкові координати для центрування лабіринту на екрані
top = (HScreen - HMaze * sizekoef) // 2
left = (WScreen - WMaze * sizekoef) // 2


# Клас для опису кожної клітинки лабіринту
class Cell:
    Walls = [0, 0, 0, 0]  # Стіни клітинки (0 - немає стіни, 1 - є стіна; порядок: праворуч, вгору, ліворуч, вниз)
    posx = 0  # Координати клітинки на екрані по осі x
    posy = 0  # Координати клітинки на екрані по осі y
    Cheese = 0  # Позначка для монет/сиру


# Клас для опису ігрових об'єктів (Pacman, привиди)
class Object:
    start = -1  # Час початку руху
    posx = 0  # Позиція на екрані по осі x
    posy = 0  # Позиція на екрані по осі y
    x = 0  # Позиція на сітці по осі x
    y = 0  # Позиція на сітці по осі y
    xprev = 0  # Попередня позиція по осі x
    yprev = 0  # Попередня позиція по осі y
    typ = "Pacman"  # Тип об'єкта (Pacman або Ghost)
    direct = 0  # Напрямок руху (0 - вправо, 1 - вгору, 2 - вліво, 3 - вниз)
    color = (0, 0, 255)  # Колір об'єкта (за замовчуванням синій)
    number = -1  # Номер об'єкта (важливо для привидів)


# Клас для відстеження зіткнень між об'єктами
class Collision:
    happened = False  # Ознака, чи відбулося зіткнення


# Функція для відображення графіки гри
def graph():
    screen.fill((0, 0, 0))  # Очищення екрану (чорний фон)

    # Малювання стін для кожної клітинки лабіринту
    for row in Cells:
        for c in row:
            # Якщо є стіна праворуч, малюємо її
            if c.Walls[0] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx + sizekoef, top + c.posy),
                                 (left + c.posx + sizekoef, top + c.posy + sizekoef))
            # Якщо є стіна вгору, малюємо її
            if c.Walls[1] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx, top + c.posy),
                                 (left + c.posx + sizekoef, top + c.posy))
            # Якщо є стіна ліворуч, малюємо її
            if c.Walls[2] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx, top + c.posy),
                                 (left + c.posx, top + c.posy + sizekoef))
            # Якщо є стіна вниз, малюємо її
            if c.Walls[3] == 1:
                pygame.draw.line(screen, (0, 255, 0), (left + c.posx, top + c.posy + sizekoef),
                                 (left + c.posx + sizekoef, top + c.posy + sizekoef))

    # Якщо потрібно показувати шлях, малюємо його
    if showpath:
        m = 1
        for i in range(WMaze):
            for j in range(HMaze):
                Entered[j][i][0] = Entered[j][i][0] + 1
                m = max(m, Entered[j][i][0])
        # Малюємо всі відвідані клітинки різними відтінками сірого
        for i in range(WMaze):
            for j in range(HMaze):
                color = (255 * Entered[j][i][0] // m, 255 * Entered[j][i][0] // m, 255 * Entered[j][i][0] // m)
                pygame.draw.circle(screen, color,
                                   (left + sizekoef * i + sizekoef // 2, top + sizekoef * j + sizekoef // 2),
                                   sizekoef // 3)
        # Малюємо червоний шлях
        for c in path:
            pygame.draw.circle(screen, (255, 0, 0),
                               (left + sizekoef * c[0] + sizekoef // 2, top + sizekoef * c[1] + sizekoef // 2),
                               sizekoef // 3)

    # Малюємо всі об'єкти гри (Pacman та привиди)
    for obj in objects:
        pygame.draw.circle(screen, obj.color, (
            left + int(sizekoef * obj.posx) + sizekoef // 2, top + int(sizekoef * obj.posy) + sizekoef // 2),
                           sizekoef // 2)
        # Перевіряємо зіткнення привидів з Pacman
        if obj.typ == "Ghost" and abs(obj.posx - player.posx) + abs(obj.posy - player.posy) < 0.2:
            collision.happened = True

    # Малюємо монетку (coin)
    pygame.draw.circle(screen, (255, 255, 0),
                       (left + sizekoef * coin[0] + sizekoef // 2, top + sizekoef * coin[1] + sizekoef // 2),
                       sizekoef // 4)


# Функція для перевірки з'єднаності клітинок лабіринту
def CheckConnection():
    used = []
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            row.append(False)
        used.append(row)

    # Використовуємо пошук у ширину (BFS) для перевірки з'єднання
    q = []
    q.append((0, 0))
    used[0][0] = True

    while (len(q) > 0):
        pos = q[0]
        x = pos[0]
        y = pos[1]
        # Рухаємося вгору, вниз, вліво, вправо, якщо немає стін
        if Cells[x][y].Walls[0] == 0 and not used[x][y + 1]:
            q.append((x, y + 1))
            used[x][y + 1] = True
        if Cells[x][y].Walls[1] == 0 and not used[x - 1][y]:
            q.append((x - 1, y))
            used[x - 1][y] = True
        if Cells[x][y].Walls[2] == 0 and not used[x][y - 1]:
            q.append((x, y - 1))
            used[x][y - 1] = True
        if Cells[x][y].Walls[3] == 0 and not used[x + 1][y]:
            q.append((x + 1, y))
            used[x + 1][y] = True
        q.pop(0)

    # Перевіряємо, чи всі клітинки з'єднані
    ans = True
    for i in used:
        for j in i:
            ans = ans and j
    return ans


# Функція генерації лабіринту за допомогою алгоритму DFS
def dfs(i, j, direc):
    used[j][i] = True
    possibles = [0, 1, 2, 3]  # Напрямки руху: вправо, вгору, вліво, вниз
    random.shuffle(possibles)  # Випадковий порядок

    for decision in possibles:
        # Рух вліво
        if decision == 2:
            if i > 0 and not used[j][i - 1]:
                dfs(i - 1, j, 0)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[2] = 1
        # Рух вправо
        if decision == 0:
            if i < WMaze - 1 and not used[j][i + 1]:
                dfs(i + 1, j, 2)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[0] = 1
        # Рух вгору
        if decision == 1:
            if j > 0 and not used[j - 1][i]:
                dfs(i, j - 1, 3)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[1] = 1
        # Рух вниз
        if decision == 3:
            if j < HMaze - 1 and not used[j + 1][i]:
                dfs(i, j + 1, 1)
                Cells[j][i].Walls[decision] = 0
            else:
                Cells[j][i].Walls[3] = 1

    if direc >= 0:
        Cells[j][i].Walls[direc] = 0


# Імовірність для визначення дій привидів
def prob():
    return math.exp(-Difficulty / 3)


# Функція оцінки шляху для алгоритму A*
def prior(x, y, x1, y1, x2, y2):
    if search == "G":  # Жадібний пошук
        return abs(x - x2) + abs(y - y2)
    if search == "A*":  # A*
        return abs(x - x2) + abs(y - y2) + (Entered[y][x][0] * 2) // 4


# BFS алгоритм пошуку
def bfs(x1, y1, x2, y2, Entered):
    # Ініціалізація
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            row.append([-1, -1, -1])  # Ініціалізація масиву Entered
        Entered.append(row)

    # Черга для BFS
    q = queue.Queue()
    q.put((x1, y1, -1, -1))  # Додаємо початкову позицію

    # Основний цикл BFS
    while not q.empty():
        x, y, xprev, yprev = q.get()

        # Якщо це не початкова клітинка, заповнюємо Entered для відновлення шляху
        if xprev != -1:
            Entered[y][x] = [Entered[y][x][0], xprev, yprev]
        else:
            Entered[y][x] = [0, -1, -1]

        # Якщо знайшли ціль
        if x == x2 and y == y2:
            break

        # Рухаємося в усі доступні напрямки
        if x > 0 and Cells[y][x].Walls[2] == 0 and Entered[y][x - 1][0] == -1:
            Entered[y][x - 1][0] = Entered[y][x][0] + 1
            q.put((x - 1, y, x, y))
        if x < WMaze - 1 and Cells[y][x].Walls[0] == 0 and Entered[y][x + 1][0] == -1:
            Entered[y][x + 1][0] = Entered[y][x][0] + 1
            q.put((x + 1, y, x, y))
        if y > 0 and Cells[y][x].Walls[1] == 0 and Entered[y - 1][x][0] == -1:
            Entered[y - 1][x][0] = Entered[y][x][0] + 1
            q.put((x, y - 1, x, y))
        if y < HMaze - 1 and Cells[y][x].Walls[3] == 0 and Entered[y + 1][x][0] == -1:
            Entered[y + 1][x][0] = Entered[y][x][0] + 1
            q.put((x, y + 1, x, y))

    # Відновлення шляху (від кінцевої до початкової точки)
    path = []
    xans, yans = x2, y2
    while xans != x1 or yans != y1:
        path.insert(0, (xans, yans))
        xans, yans = Entered[yans][xans][1], Entered[yans][xans][2]

    return path


# Пошук шляху між точками (x1, y1) і (x2, y2) з використанням A* або жадібного пошуку
def findPath(x1, y1, x2, y2, Entered):
    for i in range(HMaze):
        row = []
        for j in range(WMaze):
            row.append([-1, -1, -1])  # Ініціалізація масиву Entered
        Entered.append(row)

    if search == "BFS":
        return bfs(x1, y1, x2, y2, Entered)

    q = []
    heapq.heappush(q, (0, x1, y1, -1, -1))  # Додаємо початкову позицію

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

        # Якщо досягли мети
        if x == x2 and y == y2:
            break

        # Перевіряємо напрямки для руху
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

    # Відновлення шляху
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

# Створення лабіринту
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

# Генерація лабіринту методом Wall-Set (WS) або DFS
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


def handleCellsWS():
    Cells.clear()


def handleCellsDFS():
    Cells = []


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
    if generation == "WS":
        handleCellsWS()

    if generation == "DFS":
        handleCellsDFS()

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


# Основний цикл гри
while running:
    # Обробляємо події, що надходять від користувача та системи
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Якщо натиснуто кнопку "закрити" вікно гри
            running = False  # Завершуємо цикл гри
        elif event.type == pygame.KEYDOWN:  # Обробка натискань клавіш
            if event.key == pygame.K_DOWN:
                arrow = "Down"  # Користувач натиснув стрілку вниз
            if event.key == pygame.K_UP:
                arrow = "Up"  # Користувач натиснув стрілку вгору
            if event.key == pygame.K_LEFT:
                arrow = "Left"  # Користувач натиснув стрілку вліво
            if event.key == pygame.K_RIGHT:
                arrow = "Right"  # Користувач натиснув стрілку вправо

    # Обробляємо рух привидів
    for obj in objects:
        if obj.typ == "Ghost":  # Якщо об'єкт — привид
            if obj.start == -1 or pygame.time.get_ticks() - obj.start >= 600:
                # Якщо привид готовий до нового руху (600 мс між ходами)
                if random.uniform(0, 1) < prob():  # Випадковий рух з імовірністю, що залежить від складності гри
                    obj.start = pygame.time.get_ticks()  # Фіксуємо час початку руху
                    obj.xprev = obj.x  # Зберігаємо попередню позицію по осі x
                    obj.yprev = obj.y  # Зберігаємо попередню позицію по осі y
                    d = obj.direct  # Напрямок руху привида

                    # Якщо є стіна в напрямку руху, шукаємо новий напрямок
                    if Cells[obj.y][obj.x].Walls[d] == 1:
                        r = random.randint(0, 1)
                        if r == 0:
                            d = (d + 1) % 4  # Пробуємо поворот направо
                            if Cells[obj.y][obj.x].Walls[d] == 1:
                                d = (d + 2) % 4  # Якщо стіна, пробуємо напрямок назад
                                if Cells[obj.y][obj.x].Walls[d] == 1:
                                    d = (d + 3) % 4  # Якщо знову стіна, пробуємо напрямок наліво
                        else:
                            d = (d + 3) % 4  # Пробуємо поворот наліво
                            if Cells[obj.y][obj.x].Walls[d] == 1:
                                d = (d + 2) % 4  # Якщо стіна, пробуємо напрямок назад
                                if Cells[obj.y][obj.x].Walls[d] == 1:
                                    d = (d + 1) % 4  # Якщо знову стіна, пробуємо напрямок направо
                    obj.direct = d  # Оновлюємо напрямок руху

                    # Залежно від обраного напрямку рухаємо привида
                    if d == 0:
                        obj.x = obj.x + 1  # Рух вправо
                    elif d == 1:
                        obj.y = obj.y - 1  # Рух вгору
                    elif d == 2:
                        obj.x = obj.x - 1  # Рух вліво
                    elif d == 3:
                        obj.y = obj.y + 1  # Рух вниз
                else:
                    # Якщо привид переслідує Pacman
                    obj.start = pygame.time.get_ticks()  # Фіксуємо час початку руху
                    obj.xprev = obj.x  # Зберігаємо попередню позицію по осі x
                    obj.yprev = obj.y  # Зберігаємо попередню позицію по осі y

                    # Знаходимо шлях до Pacman'а
                    temp = []
                    temppath = findPath(obj.x, obj.y, player.x, player.y, temp)
                    temp = []
                    playerpath = findPath(player.x, player.y, coin[0], coin[1], temp)  # Шлях Pacman до монети

                    # Логіка для привида №1 - переслідує напряму
                    if len(temppath) > 0:
                        if obj.number == 0:
                            obj.x = temppath[0][0]  # Пересування по шляху
                            obj.y = temppath[0][1]
                        # Логіка для привида №2 - передбачає рух Pacman
                        elif obj.number == 1:
                            if abs(obj.x - player.x) + abs(obj.y - player.y) > 3:  # Якщо привид далеко від Pacman'а
                                targetx = player.x - (player.y - first.y)  # Передбачає позицію Pacman
                                targety = player.y + (player.x - first.x)
                            else:  # Якщо Pacman близько, переслідує напряму
                                targetx = player.x
                                targety = player.y
                            # Обмеження цілей в межах лабіринту
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
                        # Логіка для привида №3 - інший перехресний вектор для передбачення руху Pacman'а
                        elif obj.number == 2:
                            if abs(obj.x - player.x) + abs(obj.y - player.y) > 3:  # Якщо привид далеко
                                targetx = player.x + (player.y - first.y)
                                targety = player.y - (player.x - first.x)
                            else:  # Якщо Pacman близько, переслідує напряму
                                targetx = player.x
                                targety = player.y
                            # Обмеження цілей в межах лабіринту
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
                        # Логіка для інших привидів, які слідкують за Pacman
                        elif (len(temppath) <= 4):
                            obj.x = temppath[0][0]
                            obj.y = temppath[0][1]
                        else:
                            # Привид рухається до точки на шляху Pacman'а до монети
                            point = len(playerpath) // (ghostnumber - 3)  # Розрахунок точки
                            point *= (obj.number - 2)
                            point = len(playerpath) - point
                            targetx = 0
                            targety = 0
                            if (point < len(playerpath) and point >= 0):
                                targetx = playerpath[point][0]  # Вибирає цільову точку
                                targety = playerpath[point][1]
                            else:
                                targetx = player.x
                                targety = player.y
                            # Невелике випадкове зміщення для уникнення передбачуваних шляхів
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

            # Оновлюємо позицію привида, використовуючи час для плавного руху
            obj.posx = (((max(0, 600 - pygame.time.get_ticks() + obj.start)) / 600) * obj.xprev + (
                    ((min(600, pygame.time.get_ticks() - obj.start)) / 600) * obj.x))
            obj.posy = (((max(0, 600 - pygame.time.get_ticks() + obj.start)) / 600) * obj.yprev + (
                    ((min(600, pygame.time.get_ticks() - obj.start)) / 600) * obj.y))

        # Обробка руху Pacman
        if obj.typ == "Pacman":
            if obj.start == -1 or pygame.time.get_ticks() - obj.start >= 400:
                # Якщо Pacman зібрав монету, збільшуємо рахунок і переходимо на наступний рівень
                if obj.x == coin[0] and obj.y == coin[1]:
                    score += 1
                    next_level()  # Перехід на наступний рівень
                obj.start = pygame.time.get_ticks()  # Оновлюємо час початку руху
                obj.xprev = obj.x  # Зберігаємо попередню позицію по осі x
                obj.yprev = obj.y  # Зберігаємо попередню позицію по осі y

                # Рух Pacman на основі натиснутих клавіш
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
                # Якщо клавіша не змінюється, Pacman рухається в тому ж напрямку
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
                # Pacman обертається назад, якщо намагається рухатися в стіну
                if ((arrow == "Left" and obj.direct == 0) or (arrow == "Up" and obj.direct == 3) or (
                        arrow == "Down" and obj.direct == 1)):
                    obj.xprev, obj.x = obj.x, obj.xprev
                    obj.yprev, obj.y = obj.y, obj.yprev
                    obj.start = pygame.time.get_ticks() - (400 - pygame.time.get_ticks() + obj.start)
                    obj.direct += 2
                    obj.direct %= 4

            # Оновлюємо шлях Pacman до монети
            Entered = []
            path = findPath(obj.x, obj.y, coin[0], coin[1], Entered)
            # Плавний рух Pacman за часом
            obj.posx = (((max(0, 400 - pygame.time.get_ticks() + obj.start)) / 400) * obj.xprev + (
                    ((min(400, pygame.time.get_ticks() - obj.start)) / 400) * obj.x))
            obj.posy = (((max(0, 400 - pygame.time.get_ticks() + obj.start)) / 400) * obj.yprev + (
                    ((min(400, pygame.time.get_ticks() - obj.start)) / 400) * obj.y))

    # колізії з привидами перевірка
    for obj in objects:
        if obj.typ == "Ghost" and obj.x == player.x and obj.y == player.y:
            print("Final score: ", score)
            print("GAME OVER")
            running = False
            break

    graph()
    pygame.display.flip()
