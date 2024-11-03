
from src.Field.post_process import PostProcess

post_processing = PostProcess(0.4, 1)

post_processing.plot('ur')
post_processing.plot('Re(ur)')