#%%
from src.Field.post_process import PostProcess

post_process = PostProcess(0.4, 1)
#%%
post_process.plot('Im(ux)', x_max=10, r_max=3)