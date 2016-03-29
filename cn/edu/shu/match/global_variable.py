# 主题模型配置文件地址
config_path = './topic/config.json'
# 算法配置文件地址
algorithm_config_path = './config/algorithm.json'
# 过滤的行业类别名
default_industry_name = '默认'
# 分割需求和服务的符号
split_symbol = '[,|，|.|。|!|！|?|？|;|；|\n|\t|\s]'
# 不进行分割的需求和服务文件在需求和服务表中索引
require_no_segment = [2, 4]
provide_no_segment = [2, 4]
# 主题中词概率低于此值不显示
minimum_probability = 0
# 阈值法分割阈值
cos_segment_threshold = 0.5
# 匹配度阈值
match_threshold = 0.5
# 自动匹配度最小阈值
dynamic_match_min_threshold = 0.2
