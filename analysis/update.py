from evaluation import *

import datetime

indexs = {}
indexs.update(scale_index)
indexs.update(primary_industry_index)
indexs.update(other_industry_index)
indexs.update(other_industry_index)
indexs.update(other_subject_index)
indexs.update(style_index)
indexs.update(overseas_index)

for index in indexs:
    update_to_lastest(index, 'day')
    update_to_lastest(index, 'month')

# for index in indexs:
#     local_recalculate(index, 'day')

# update_to_lastest('000992.SH', 'day')
# update_to_lastest('000992.SH', 'month')