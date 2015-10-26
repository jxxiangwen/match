from gensim import corpora,models,similarities
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from gensim import corpora, models, similarities
import logging
import nltk
import time

#logging.basicConfig(format=' %(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)
start = time.clock()

#文件预处理
file = open('coursera_corpus','r',encoding= 'utf-8')
courses = [line.strip() for line in file]
courses_name = [course.split('\t')[0] for course in courses]


#分词
texts_tokenized = [[word.lower() for word in word_tokenize(document)] for document in courses]
 
#去除停用词
english_stopwords = stopwords.words('english')
texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in texts_tokenized]
#去除标点符号
english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
texts_filtered = [[word for word in document if not word in english_punctuations] for document in texts_filtered_stopwords]
 
#词干化
st = LancasterStemmer()
texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]
 
 
#去除过低频词
all_stems = sum(texts_stemmed, [])
stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]

 
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]     #doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
 
#拍脑袋的：训练topic数量为10的LSI模型
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
index = similarities.MatrixSimilarity(lsi[corpus])     # index 是 gensim.similarities.docsim.MatrixSimilarity 实例

#选择一个基准数据
ml_course = texts[210]
ml_bow = dictionary.doc2bow(ml_course)
#在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
ml_lsi = lsi[ml_bow]#ml_lsi 形式如 (topic_id, topic_value)
print(ml_lsi)

sims = index[ml_lsi]#sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi
sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])#排序，为输出方便
print(sort_sims[0:10])#查看结果

end = time.clock()
print("time: %f s" % (end - start))

