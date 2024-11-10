from src.Field.post_process import PostProcess

post_process = PostProcess(0.4, 1, epsilon=0.005, t=0)

post_process.plot_field('ux', 'total', x_max=8, r_max=2)

