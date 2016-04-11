######################################################表配置地址#######################################
# Mongodb配置文件地址
mongodb_path = './config/mongodb.json'
# 算法配置文件地址
algorithm_config_path = './config/algorithm.json'
# 需求表配置文件地址
require_table_path = './config/require_table.json'
# 服务表配置文件地址
provide_table_path = './config/provide_table.json'
######################################################主题模型配置地址#######################################
# 主题模型配置文件地址
config_path = './topic/config/config.json'
# 词典训练配置文件地址
dictionary_config_path = './topic/config/dictionary_config.json'
# 语料库训练配置文件地址
corpus_config_path = './topic/config/corpus_config.json'
# 临时语料库训练配置文件地址
temp_corpus_config_path = './topic/config/temp_corpus_config.json'
# lsi训练配置文件地址
lsi_config_path = './topic/config/lsi_config.json'
# lda训练配置文件地址
lda_config_path = './topic/config/lda_config.json'
# hdp训练配置文件地址
hdp_config_path = './topic/config/hdp_config.json'
# hdp训练配置文件地址
insert_config_path = './topic/config/insert_config.json'
######################################################项目相关配置地址#######################################
# 过滤的行业类别名
default_industry_name = '默认'
# 分割需求和服务的符号
split_symbol = '[.|。|!|！|?|？|\n|\t|\s]'
# 不进行分割的需求和服务文件在需求和服务表中索引
require_no_segment = (2, 4)
provide_no_segment = (2, 4)
# 主题中词概率低于此值不显示
minimum_probability = 0
# 阈值法分割阈值
cos_segment_threshold = 0.5
# 匹配阈值最低线
cos_match_threshold = 0.5
# 匹配度阈值
match_threshold = 0.1
# 自动匹配度最小阈值
dynamic_match_min_threshold = 0.1
# 需求正常状态
require_normal_status = (1, 2)
# 服务正常状态
provide_normal_status = (1, 2)
