#! /usr/bin/env python
# encoding: utf-8

"""
@Author:Lich
@Time:  2017/11/29 10:35
@Description: 文本处理，构建自己的新闻语料库
"""


from collections import Counter
from nltk.corpus import *
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import *
from numpy import *
import nltk
import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'Lich'

'''
文本处理，包括分词，去停用词、去无用词、词形还原等
'''


def text_parse(input_text):
    sentence = input_text.lower()
    lemmatizer = WordNetLemmatizer()  # 词形还原
    vocab_set = set([])  # 记录所有出现的单词
    special_tag = ['.', ',', '!', '#', '(', ')', '*', '`', ':', '?', '"', '‘', '’']
    pattern = r""" (?x)(?:[A-Z]\.)+ 
                  | \d+(?:\.\d+)?%?\w+
                  | \w+(?:[-']\w+)*
                  | (?:[,.;'"?():-_`])"""

    word_list = regexp_tokenize(sentence, pattern)
    filter_word = [w for w in word_list if w not in stopwords.words('english') and w not in special_tag]  # 去停用词和特殊标点符号
    word_tag = nltk.pos_tag(filter_word)  # 词性标注，返回标记列表[('Codeine', 'NNP'), ('15mg', 'CD')]
    res_word_list = []
    for i in range(0, len(word_tag)):  # 去掉副词、介词、小品词、疑问词、代词、人称代词、所有格代名词等
        if word_tag[i][1] == 'TO' or word_tag[i][1] == 'RB' or word_tag[i][1] == 'RBR' \
                or word_tag[i][1] == 'RBRS' or word_tag[i][1] == 'UH' or word_tag[i][1] == 'WDT' \
                or word_tag[i][1] == 'WP' or word_tag[i][1] == 'WP$' or word_tag[i][1] == 'WRB' \
                or word_tag[i][1] == 'SYM' or word_tag[i][1] == 'RP' or word_tag[i][1] == 'PRP' \
                or word_tag[i][1] == 'PRP$' or word_tag[i][1] == 'CD':
            pass
        else:
            word = lemmatizer.lemmatize(word_tag[i][0])
            res_word_list.append(word)
            vocab_set.add(word)
    return res_word_list, vocab_set


'''
从挑选的各类文档中提取出能够代表各类文档的特征集合，输入的各类文档数目越多，特征集合越完善，分类效果越好；
提取文本特征，TF-IDF算法（这里利用词形还原（也可以利用词干提取））
返回每篇文章的特征值集合[['a','b'],['c','d'],...,['y',['z']]]
'''


def get_doc_features(input_matrix_data, vocab_set, threshold=0.008):
    input_matrix = input_matrix_data
    doc_nums = len(input_matrix)  # 输入的文档总数
    words_tf, words_count_matrix = calculate_tf(input_matrix)  # 计算词频
    n_contain_dict = calculate_d(words_count_matrix, vocab_set)  # 计算包含某单词a 的文档数目
    words_idf = calculate_idf(doc_nums, n_contain_dict)  # 计算逆文档
    words_tf_idf, sorted_tf_idf = calculate_tf_idf(doc_nums, words_tf, words_idf)  # 计算一篇文档中单词的tf-idf值

    # 取特征：设置阈值,取tf-idf值大于0.008,这个阈值需要根据分类结果进行调整
    doc_features = []
    for i in range(0, len(sorted_tf_idf)):
        tmp = []
        for tuple_w in sorted_tf_idf[i]:
            if tuple_w[1] >= threshold:
                tmp.append(tuple_w[0])
        doc_features.append(tmp)
        del tmp
    return doc_features


'''
计算TF-IDF
'''


def calculate_tf_idf(doc_nums, words_tf, words_idf):
    res = []
    sorted_res = []
    for i in range(0, doc_nums):
        tf_idf_dict = {}
        for word in words_tf[i]:
            tf_idf_dict[word] = (words_tf[i][word] * words_idf[word])
        res.append(tf_idf_dict)
        sorted_res.append(sorted(tf_idf_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True))  # 按照tf-idf 值从大到小进行排序
        del tf_idf_dict
    return res, sorted_res


'''
计算包含某单词a 的文档数目
'''


def calculate_d(words_count_matrix, vocab_set):
    n_contain_dict = {}  # 包含此单词的文档数目
    for word in vocab_set:
        n = sum(1 for lst in words_count_matrix if word in lst)
        n_contain_dict[word] = n
    return n_contain_dict


'''
计算词频,一个单词在某个文档A中出现的频率
'''


def calculate_tf(input_matrix):
    res_list = []
    words_count = []
    for lst in input_matrix:
        words_count.append(Counter(lst))

    for lst in words_count:
        tf_dict = {}
        for word in lst.keys():
            tf_dict[word] = lst[word] / float(sum(lst.values()))  # 计算词频
        res_list.append(tf_dict)
        del tf_dict
    return res_list, words_count


'''
计算逆文档频率
'''


def calculate_idf(doc_nums, n_contain_dict):
    idf_dict = {}
    for word in n_contain_dict.keys():
        idf_dict[word] = log(doc_nums / (n_contain_dict[word]))
    return idf_dict


'''
返回每个类型的特征集合，建立自己的语料库
'''


def get_class_features():
    post_list = []
    vocab_set = set([])
    dirs = ['env', 'eco', 'pol']
    features = []
    categories = []
    env = []
    eco = []
    pol = []
    for dir_name in dirs:
        for i in range(1, 6):
            res_word_list, doc_set = text_parse(open(r'G:\Repositories\ML--Native-Bayes\material\\' + dir_name + r'\%d.txt' % i).read().decode('utf-8'))
            # open(u'/Users/lch/Desktop/pycharm/Bayes/material/' + name + u'/%d.txt' % i).read().decode('utf-8'))
            post_list.append(res_word_list)
            vocab_set = vocab_set | doc_set
            categories.append(dir_name)
    print '文本去除停用词、词形还原后还剩余', len(list(vocab_set)), '个不重复单词。'
    docs_features = get_doc_features(post_list, vocab_set, 0.015)
    for i in range(0, len(categories)):
        if categories[i] == 'env':
            env.extend(docs_features[i])
        elif categories[i] == 'eco':
            eco.extend(docs_features[i])
        elif categories[i] == 'pol':
            pol.extend(docs_features[i])
        else:
            pass

    features.append((env, 'env'))
    features.append((eco, 'eco'))
    features.append((pol, 'pol'))
    return features