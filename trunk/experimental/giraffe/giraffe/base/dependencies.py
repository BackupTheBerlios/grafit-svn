
def dfs(graph, start, rlevel=0, seen = None):
    if seen is None: 
        seen = {}
    seen[start] = 1
    for v in graph[start]:
        is_back = v in seen
        seen[v] = True
        yield (start, v), is_back, rlevel
        if not is_back:
            if v in graph:
                for e in dfs(graph, v, rlevel+1, seen):
                    yield e

def has_cycle(graph):
    for e, is_back, level in dfs(graph, 1):
        if is_back:
            return True
    return False

class Dependencies(object):
    def __init__(self):
        self.graph = {}

    def add(self, obj, dep):
        if obj in self.graph:
            self.graph[obj].append(dep)
        else:
            self.graph[obj] = [dep]

    def will_create_cycle(self, obj, dep):
        self.add(obj, dep)
        c = self.has_cycle()
        self.remove(obj, dep)
        return c

    def remove(self, obj, dep):
        self.graph[obj].remove(dep)
        if self.graph[obj] == []:
            del self.graph[obj]

    def has_cycle(self):
        return has_cycle(self.graph)

    def deps(self, obj):
        return self.graph[obj]


if __name__ == '__main__':
    G = {
            1:      (2,3),
            2:      (3,5),
            3:      (4,),
            4:      (6,),
            5:      (2,6),
            6:      (1,),
            }

    deps = Dependencies()

    for f, t in G.iteritems():
        for o in t:
            print deps.will_create_cycle(f, o)
            deps.add(f, o)

    print deps.has_cycle()
