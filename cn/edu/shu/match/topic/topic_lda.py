import numpy as np
import lda
import lda.datasets

def test():
    '''
    lda包用法
    :return:
    '''
    train_data = lda.datasets.load_reuters()
    vocab = lda.datasets.load_reuters_vocab()
    title = lda.datasets.load_reuters_titles()

    model = lda.LDA(n_topics=30, n_iter=3000, random_state=1)
    model.fit(train_data)
    topic_word = model.topic_word_
    doc_topic = model.doc_topic_
    n_top_words = 8
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))


if __name__ == '__main__':
    test()