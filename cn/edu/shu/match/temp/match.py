from gensim import corpora,models,similarities
import logging

#logging.basicConfig(format=' %(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)

documents = ["Shipment of gold damaged in a fire","Delivery of silver arrived in a silver truck","Shipment of gold arrived in a truck"]
texts = [[word for word in document.lower().split()] for document in documents]#将单词小写化
print("texts : ")
print(texts)

dictionary = corpora.Dictionary(texts)#生成词袋模型
print("dictionary.token2id :")
print(dictionary.token2id)

corpus = [dictionary.doc2bow(text) for text in texts]#将字符串表示的文档转换为ID表示的文档
print("corpus :")
print(corpus)

tfidf = models.TfidfModel(corpus)#生成TF-IDF模型
print("tfidf :")
print(tfidf)

print(type(tfidf))
print(type(corpus))
corpus_tfidf = tfidf[corpus]
for doc in corpus_tfidf:
    print(doc)
print(tfidf.dfs)
print(tfidf.idfs)

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary,num_topics=2)#生成lsi模型
lsi.print_topics(2)
corpus_lsi = lsi[corpus_tfidf]

for doc in corpus_lsi:
    print(doc)

lda = models.LdaModel(corpus_tfidf, id2word=dictionary,num_topics=2)#生成lda模型
lda.print_topics(2)
corpus_lda = lda[corpus_tfidf]

for doc in corpus_lda:
    print(doc)

index = similarities.MatrixSimilarity(lsi[corpus])#建立索引

query = "gold silver truck"#查询语句
query_bow = dictionary.doc2bow(query.lower().split())#生成词袋模型
print("query_bow : ")
print(query_bow)

query_lsi = lsi[query_bow]
print("query_lsi : ")
print(query_lsi)

sims = index[query_lsi]
print(list(enumerate(sims)))

sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
print(sort_sims)
