#%%
from homework import SafePath
for i in range(1,51):
    inp = 'input\input'+str(i)+'.txt'
    sp = SafePath(inp)
    print(i,sp.compute_safe_paths())