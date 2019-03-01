import math
import jieba
import jieba.posseg as psg
import operator

# 停用词表加载方法
def get_stopword_list():
    # 停用词表存储路径，每一行为一个词，按行读取进行加载
    # 进行编码转换确保匹配准确率
    stop_word_path = './stop_word.txt'
    stopword_list = [sw.replace('\n', '') for sw in open(stop_word_path).readlines()]
    return stopword_list


# 分词方法，调用结巴接口
def seg_to_list(sentence, pos=False):
    if not pos:
        # 不进行词性标注的分词方法
        seg_list = jieba.cut(sentence)
    else:
        # 进行词性标注的分词方法
        seg_list = psg.cut(sentence)
    return seg_list


# 去除干扰词,并且过滤非名词
def word_filter(seg_list, pos=False):
    stopword_list = get_stopword_list()
    filter_list = []
    # 根据POS参数选择是否词性过滤
    # 不进行词性过滤，则将词性都标记为n，表示全部保留
    for seg in seg_list:
        # 不进行词性过滤
        if not pos:
            word = seg  #
            flag = 'n'  #
        # 进行词性过滤
        else:
            word = seg.word
            flag = seg.flag
        # 名词都是以n开头的
        if not flag.startswith('n'):  # 过滤掉非名词
            continue
        # 过滤停用词表中的词，以及长度为<2的词, 长度小于2,即单独成词,无意义
        if not word in stopword_list and len(word) > 1:
            filter_list.append(word)
    return filter_list


# 数据加载，pos为是否词性标注的参数，corpus_path为数据集路径
def load_data(pos=False, corpus_path='./corpus.txt'):
    # 调用上面方式对数据集进行处理，处理后的每条数据仅保留非干扰词
    doc_list = []
    with open(corpus_path, 'r') as fileobject:
        for line in fileobject.readlines():
            content = line.strip()
            seg_list = seg_to_list(content, pos)  # 分词
            filter_list = word_filter(seg_list, pos)
            doc_list.append(filter_list)
    return doc_list

# idf值统计方法
def train_idf(doc_list):
    idf_dic = {}
    # 总文档数
    tt_count = len(doc_list)

    # 每个词出现的文档数
    for doc in doc_list:
        for word in set(doc):
            idf_dic[word] = idf_dic.get(word, 0.0) + 1.0

    # 按公式转换为idf值，分母加1进行平滑处理
    for k, v in idf_dic.items():
        idf_dic[k] = math.log(tt_count / (1.0 + v))

    # 对于没有在字典中的词，默认其仅在一个文档出现，得到默认idf值,进行平滑处理
    default_idf = math.log(tt_count / (1.0))
    return idf_dic, default_idf

# TF-IDF类
class TfIdf(object):
    def __init__(self, idf_dic, default_idf, word_list, keyword_num):
        '''
        四个参数分别是
        :param idf_dic: 训练好的idf字典
        :param default_idf: 默认idf值
        :param word_list: 处理后的待提取文本,已经分好词了
        :param keyword_num: 关键词数量
        '''
        self.idf_dic = idf_dic
        self.default_idf =default_idf
        self.word_list = word_list
        self.tf_dic = self.get_tf_dic()
        self.keyword_num = keyword_num

    # 统计tf值
    def get_tf_dic(self):
        tf_dic = {}
        for word in self.word_list:
            tf_dic[word] = tf_dic.get(word, 0.0) + 1.0

        tt_count = len(self.word_list)  # 文本总长度
        for k, v in tf_dic.items():  # 计算每一个词的tf值
            tf_dic[k] = float(v) / tt_count
        return tf_dic

    # 按公式计算tf-idf
    def get_tfidf(self):
        tfidf_dic = {}
        for word in self.word_list:
            idf = self.idf_dic.get(word, self.default_idf)
            tf = self.tf_dic.get(word, 0)

            tfidf = tf * idf
            tfidf_dic[word] = tfidf

        # 根据tf-idf排序，去排名前keyword_num的词作为关键词
        for k, v in sorted(tfidf_dic.items(), key=operator.itemgetter(1), reverse=True)[:self.keyword_num]:
            print(k + "/ ", end='')
        print()


# tfidf函数接口
def tfidf_extract(word_list, corpus_path='./corpus.txt',pos=False, keyword_num=10):
    doc_list = load_data(pos,corpus_path)
    idf_dic, default_idf = train_idf(doc_list)
    tfidf_model = TfIdf(idf_dic, default_idf, word_list, keyword_num)
    tfidf_model.get_tfidf()


if __name__ == '__main__':
    text = '6月19日,《2012年度“中国爱心城市”公益活动新闻发布会》在京举行。' + \
           '中华社会救助基金会理事长许嘉璐到会讲话。基金会高级顾问朱发忠,全国老龄' + \
           '办副主任朱勇,民政部社会救助司助理巡视员周萍,中华社会救助基金会副理事长耿志远,' + \
           '重庆市民政局巡视员谭明政。晋江市人大常委会主任陈健倩,以及10余个省、市、自治区民政局' + \
           '领导及四十多家媒体参加了发布会。中华社会救助基金会秘书长时正新介绍本年度“中国爱心城' + \
           '市”公益活动将以“爱心城市宣传、孤老关爱救助项目及第二届中国爱心城市大会”为主要内容,重庆市' + \
           '、呼和浩特市、长沙市、太原市、蚌埠市、南昌市、汕头市、沧州市、晋江市及遵化市将会积极参加' + \
           '这一公益活动。中国雅虎副总编张银生和凤凰网城市频道总监赵耀分别以各自媒体优势介绍了活动' + \
           '的宣传方案。会上,中华社会救助基金会与“第二届中国爱心城市大会”承办方晋江市签约,许嘉璐理' + \
           '事长接受晋江市参与“百万孤老关爱行动”向国家重点扶贫地区捐赠的价值400万元的款物。晋江市人大' + \
           '常委会主任陈健倩介绍了大会的筹备情况。'

    pos = True
    seg_list = seg_to_list(text, pos)
    filter_list = word_filter(seg_list, pos)
    print('TF-IDF模型结果：')
    tfidf_extract(filter_list,'./news/社会新闻/corpus.txt')
