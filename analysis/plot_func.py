from evaluation import *

# 一系列指数pe
plot_index_list(list(scale_index.values()), line_name.pe,
        y_min = 0, y_max = 80, 
        y_interval = 5)