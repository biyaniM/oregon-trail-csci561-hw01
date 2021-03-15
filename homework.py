#%%
import math
import queue
from collections import deque
import re
class SafePath(object):
    def __init__(self,inp:str) -> None:
        f=open(inp,'r').read()
        lines = f.split('\n')
        self.ip=str(inp)
        self.algo = str(lines[0])
        self.w,self.h = [int(i) for i in lines[1].split(' ')]
        self.start = tuple([int(i) for i in lines[2].split(' ')])
        self.m_max = int(lines[3])
        self.n = int(lines[4])
        self.settling_site_locations =[tuple([int(j) for j in i.split(' ')[:2]]) for i in lines[5:5+self.n]]
        self.maze=[[int(j) for j in i.split()[:self.w]] for i in lines[5+self.n:5+self.n+self.h]]
        self.op=re.findall(r'\d+',self.ip)[0]

    def format_paths(self,sol)->str:
        return '\n'.join(['FAIL' if not s else ' '.join([str(x[0])+','+str(x[1]) for x in s]) for s in sol])

    def compute_safe_paths(self):
        op_path='output/output'+self.op+'.txt'
        if self.algo=='A*':
            sol = AStar(self.ip).solution()
            open(op_path,'w').write(self.format_paths(sol))
            return sol
        elif self.algo=='BFS':
            sol = BFS(self.ip).solution()
            open(op_path,'w').write(self.format_paths(sol))
            return sol
        elif self.algo=='UCS':
            sol = UCS(self.ip).solution()
            open(op_path,'w').write(self.format_paths(sol))
            return sol
        else:
            open('output.txt','w').write('Wrong Algorithm Input')
    
    def get_input(self):
        return self.maze

class BFS(SafePath):
    class Node:
        def __init__(self,parent=None,position=None) -> None:
            self.parent=parent
            self.position=position
    
        def __eq__(self, o: object) -> bool:
            return self.position==o.position
    def trace_path(self,curr) -> list:
        path=[]
        while curr:
            path.append(curr.position)
            curr=curr.parent
        return path[::-1]        
    def __init__(self,ip) -> None:
        super().__init__(ip)
        self.__moves=[(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def is_bfs_move_valid(self,x_from,x_move,y_from,y_move) -> bool:
        if (x_from+x_move>=0 and x_from+x_move<=self.w-1 and y_from+y_move>=0 and y_from+y_move<=self.h-1) == False:
            return False # within terrain range
        if (abs((abs(self.maze[y_from+y_move][x_from+x_move]) if self.maze[y_from+y_move][x_from+x_move]<0 else 0) - (abs(self.maze[y_from][x_from]) if self.maze[y_from][x_from]<0 else 0)) <= self.m_max) == False:
            return False # wagon can climb
        #if len([v for v in visited1 if v.position==(x_from+x_move,y_from+y_move)])>0: return False
        return True
        
    def solution(self) -> list:
        result=[]
        for end in [self.Node(None,e) for e in self.settling_site_locations]:
            q=deque()
            q.append(self.Node(None,self.start))
            path_found=False
            visited=set()
            while q:
                pos=q.popleft()
                visited.add(pos.position)
                if pos == end: # if end node found in the path
                    result.append(self.trace_path(pos))
                    path_found=True
                    break
                for move in self.__moves:
                    if self.is_bfs_move_valid(pos.position[0],move[0],pos.position[1],move[1]):
                        new_position=(pos.position[0]+move[0],pos.position[1]+move[1])
                        if new_position in visited: continue
                        new_node=self.Node(pos,new_position)
                        visited.add(new_position)
                        q.append(new_node)
            if not path_found: result.append([])
        return result

class UCS(SafePath):

    class Node:
        def __init__(self,parent=None,position=None,cost=0) -> None:
            self.parent=parent
            self.position=position
            self.cost=0
        def __gt__(self,o:object) -> bool:
            return self.cost>o.cost
        def __lt__(self,o:object) -> bool:
            return self.cost<o.cost
        def __ge__(self,o:object) -> bool:
            return self.cost>=o.cost
        def __le__(self,o:object) -> bool:
            return self.cost<=o.cost
        def __eq__(self, o: object) -> bool:
            return self.position==o.position

    def __init__(self,ip) -> None:
        super().__init__(ip)
        self.__linear_moves=[(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.__diagonal_moves=[(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def trace_path(self,curr) -> list:
        path=[]
        while curr:
            path.append(curr.position)
            curr=curr.parent
        #print(path[::-1])
        return path[::-1]
    
    def is_ucs_move_valid(self,x_from,x_move,y_from,y_move) -> bool:
        if (x_from+x_move>=0 and x_from+x_move<=self.w-1 and y_from+y_move>=0 and y_from+y_move<=self.h-1) == False:
            return False # within terrain range
        if (abs((abs(self.maze[y_from+y_move][x_from+x_move]) if self.maze[y_from+y_move][x_from+x_move]<0 else 0) - (abs(self.maze[y_from][x_from]) if self.maze[y_from][x_from]<0 else 0)) <= self.m_max) == False:
            return False # wagon can climb
        return True
    
    def solution(self) -> list:
        result=[]
        for end in [self.Node(None,x,float('inf')) for x in self.settling_site_locations]:
            q=queue.PriorityQueue()
            q.put(self.Node(None,self.start,0))
            path_found=False
            visited=set()
            while not q.empty():
                pos=q.get()
                cost = pos.cost
                visited.add(pos.position)
                #print(pos.position)
                #print(q.qsize())
                if pos==end:
                    #print(pos.cost)
                    result.append(self.trace_path(pos))
                    path_found=True
                    break
                for move in self.__linear_moves:
                    if self.is_ucs_move_valid(pos.position[0],move[0],pos.position[1],move[1]):
                        new_position=(pos.position[0]+move[0],pos.position[1]+move[1])
                        if new_position not in visited: 
                            #continue
                            visited.add(new_position)
                            new_node=self.Node(pos,new_position)
                            new_node.cost=cost+10
                            q.put(new_node)
                for move in self.__diagonal_moves:
                    if self.is_ucs_move_valid(pos.position[0],move[0],pos.position[1],move[1]):
                        new_position=(pos.position[0]+move[0],pos.position[1]+move[1])
                        if new_position not in visited: 
                            #continue
                            visited.add(new_position)
                            new_node=self.Node(pos,new_position)
                            new_node.cost=cost+14
                            q.put(new_node)
                #print('\t',visited)
            if not path_found: result.append([])
        return result

class AStar(SafePath):
    class Node:
        def __init__(self,parent=None,position=None) -> None:
            self.parent=parent
            self.position=position
            self.g=0 # cost from start to current
            self.h=0 # cost from current to end
            self.f=0 # total cost of present node f = g + h
    
        def __eq__(self, o: object) -> bool:
            return self.position==o.position
        def __gt__(self,o:object) -> bool:
            return self.f>o.f
        def __lt__(self,o:object) -> bool:
            return self.f<o.f
        def __ge__(self,o:object) -> bool:
            return self.f>=o.f
        def __le__(self,o:object) -> bool:
            return self.f<=o.f
        def __eq__(self, o: object) -> bool:
            return self.position==o.position

    def __init__(self,inp) -> None:
        super().__init__(inp)
        self.inp=inp
        self.__linear_moves=[(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.__diagonal_moves=[(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def is_astar_neighbor_valid(self,x_from,x_move,y_from,y_move) -> bool:
        if (x_from+x_move>=0 and x_from+x_move<=self.w-1 and y_from+y_move>=0 and y_from+y_move<=self.h-1) == False:
            return False# within terrain range
        if (abs((abs(self.maze[y_from+y_move][x_from+x_move]) if self.maze[y_from+y_move][x_from+x_move]<0 else 0) - (abs(self.maze[y_from][x_from]) if self.maze[y_from][x_from]<0 else 0)) <= self.m_max) == False :
            return False# wagon can climb
        return True

    def trace_path(self,curr) -> list:
        path=[]
        while curr:
            path.append(curr.position)
            curr=curr.parent
        return path[::-1]

    def solution(self) ->list:
        result=[]
        for end in [self.Node(None,i) for i in self.settling_site_locations]:
            frontier = queue.PriorityQueue()
            start = self.Node(None,self.start)
            frontier.put(start)
            path_found=False
            visited=set()
            open_list={}
            open_list[start.position]=0
            while not frontier.empty():
                current_node=frontier.get()
                visited.add(current_node.position)
                if current_node.position in open_list: del open_list[current_node.position]
                if current_node==end:
                    print(current_node.g)
                    result.append(self.trace_path(current_node))
                    path_found=True
                    break
                linear_neighbors=[]
                for move in self.__linear_moves:
                    if self.is_astar_neighbor_valid(current_node.position[0],move[0],current_node.position[1],move[1]):
                        new_linear_neighbor=self.Node(current_node,(current_node.position[0]+move[0],current_node.position[1]+move[1]))
                        new_linear_neighbor.g=float('inf')
                        new_linear_neighbor.h=float('inf')
                        new_linear_neighbor.f=float('inf')
                        linear_neighbors.append(new_linear_neighbor)
                for neighbor in linear_neighbors:
                    if neighbor.position in visited: continue
                    #visited.add(neighbor.position)
                    current_m=self.maze[current_node.position[1]][current_node.position[0]]
                    neighbor_m=self.maze[neighbor.position[1]][neighbor.position[0]]
                    neighbor_rocky=neighbor_m<0
                    current_rocky=current_m<0
                    mud_level= 0 if neighbor_rocky else self.maze[neighbor.position[1]][neighbor.position[0]] 
                    height_change=abs(abs(neighbor_m if neighbor_rocky else 0)-abs(current_m if current_rocky else 0))
                    neighbor.g=current_node.g+10+mud_level+height_change
                    if neighbor.position in open_list:
                        if open_list[neighbor.position]<=neighbor.g:
                            continue
                    #! Check if Euclidean has to be changed
                    neighbor.h=int(math.sqrt((neighbor.position[0]-current_node.position[0])**2+(neighbor.position[1]-current_node.position[1])**2))
                    neighbor.f=neighbor.g+neighbor.h
                    frontier.put(neighbor)
                    open_list[neighbor.position]=neighbor.g
                diagonal_neighbors=[]
                for move in self.__diagonal_moves:
                    if self.is_astar_neighbor_valid(current_node.position[0],move[0],current_node.position[1],move[1]):
                        new_diagonal_neighbor=self.Node(current_node,(current_node.position[0]+move[0],current_node.position[1]+move[1]))
                        new_diagonal_neighbor.g=float('inf')
                        new_diagonal_neighbor.h=float('inf')
                        new_diagonal_neighbor.f=float('inf')
                        diagonal_neighbors.append(new_diagonal_neighbor)
                for neighbor in diagonal_neighbors:
                    if neighbor.position in visited: continue
                    #visited.add(neighbor.position)
                    current_m=self.maze[current_node.position[1]][current_node.position[0]]
                    neighbor_m=self.maze[neighbor.position[1]][neighbor.position[0]]
                    neighbor_rocky=neighbor_m<0
                    current_rocky=current_m<0
                    mud_level= 0 if neighbor_rocky else self.maze[neighbor.position[1]][neighbor.position[0]] 
                    height_change=abs(abs(neighbor_m if neighbor_rocky else 0)-abs(current_m if current_rocky else 0))
                    neighbor.g=int(current_node.g+14+mud_level+height_change)
                    if neighbor.position in open_list:
                        if open_list[neighbor.position]<=neighbor.g:
                            continue
                    #! Check if Euclidean has to be changed
                    neighbor.h=int(math.sqrt((neighbor.position[0]-current_node.position[0])**2+(neighbor.position[1]-current_node.position[1])**2))
                    neighbor.f=neighbor.g+neighbor.h
                    frontier.put(neighbor)
                    open_list[neighbor.position]=neighbor.g
            if not path_found: result.append([])
        return result

'''
if __name__ == '__main__':
    #import time
    #t1=time.time()
    sp=SafePath('input.txt')
    sp.compute_safe_paths()
    #print(time.time()-t1)
'''