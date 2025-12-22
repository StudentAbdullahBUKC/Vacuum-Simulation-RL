from collections import deque
from config import *

def bfs(env, start, targets):
    targets = set(tuple(t) for t in targets)
    q = deque([(start, [])])
    visited = set([start])

    while q:
        (x, y), path = q.popleft()
        if (x, y) in targets:
            return path

        for dx, dy in [(-1,0),(1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < env.rows and 0 <= ny < env.cols:
                if (nx, ny) not in visited and env.grid[nx][ny] not in OBSTACLES:
                    visited.add((nx, ny))
                    q.append(((nx, ny), path+[(nx, ny)]))
    return []
