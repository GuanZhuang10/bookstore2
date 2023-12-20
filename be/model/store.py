import logging
from sqlalchemy import Column, String, Text, BLOB, Boolean, Integer, DateTime, ForeignKey, create_engine, \
    PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from fe.access import book
import jieba
import pymongo

Base = declarative_base()
import re


stop_words = {'打开天窗说亮话', '到目前为止', '赶早不赶晚', '常言说得好', '何乐而不为', '毫无保留地', '由此可见', '这就是说', '这么点儿', '综上所述', '总的来看',
                  '总的来说', '总的说来', '总而言之', '相对而言', '除此之外', '反过来说', '恰恰相反', '如上所述', '换句话说', '具体地说', '具体说来', '另一方面',
                  '与此同时', '一则通过', '毫无例外', '不然的话', '从此以后', '从古到今', '从古至今', '从今以后', '大张旗鼓', '从无到有', '从早到晚', '弹指之间',
                  '不亦乐乎', '不知不觉', '不止一次', '不择手段', '不可开交', '不可抗拒', '不仅仅是', '不管怎样', '挨家挨户', '长此下去', '长话短说', '除此而外',
                  '除此以外', '除此之外', '得天独厚', '川流不息', '长期以来', '挨门挨户', '挨门逐户', '多多少少', '多多益善', '二话不说', '更进一步', '二话没说',
                  '分期分批', '风雨无阻', '归根到底', '归根结底', '反之亦然', '大面儿上', '倒不如说', '成年累月', '换句话说', '或多或少', '简而言之', '接连不断',
                  '尽如人意', '尽心竭力', '尽心尽力', '尽管如此', '据我所知', '具体地说', '具体来说', '具体说来', '近几年来', '每时每刻', '屡次三番', '三番两次',
                  '三番五次', '三天两头', '另一方面', '老老实实', '年复一年', '恰恰相反', '顷刻之间', '穷年累月', '千万千万', '日复一日', '如此等等', '如前所述',
                  '如上所述', '一方面', '切不可', '顷刻间', '全身心', '另方面', '另一个', '猛然间', '默默地', '就是说', '近年来', '尽可能', '接下来', '简言之',
                  '急匆匆', '即是说', '基本上', '换言之', '充其极', '充其量', '暗地里', '反之则', '比如说', '背地里', '背靠背', '并没有', '不得不', '不得了',
                  '不得已', '不仅仅', '不经意', '不能不', '不外乎', '不由得', '不怎么', '不至于', '策略地', '差不多', '常言道', '常言说', '多年来', '多年前',
                  '差一点', '敞开儿', '抽冷子', '大不了', '反倒是', '反过来', '大体上', '当口儿', '倒不如', '怪不得', '动不动', '看起来', '看上去', '看样子',
                  '够瞧的', '到了儿', '呆呆地', '来不及', '来得及', '到头来', '连日来', '于是乎', '为什么', '这会儿', '换言之', '那会儿', '那么些', '那么样',
                  '什么样', '反过来', '紧接着', '就是说', '要不然', '要不是', '一方面', '以至于', '自个儿', '自各儿', '之所以', '这么些', '这么样', '怎么办',
                  '怎么样', '谁知', '顺着', '似的', '虽然', '虽说', '虽则', '随着', '所以', '他们', '他人', '它们', '她们', '倘或', '倘然', '倘若', '倘使',
                  '要么', '要是', '也罢', '也好', '以便', '依照', '以及', '以免', '以至', '以致', '抑或', '因此', '因而', '因为', '由于', '有的', '有关',
                  '有些', '于是', '与否', '与其', '越是', '云云', '一般', '一旦', '一来', '一切', '一样', '同时', '万一', '为何', '为了', '为着', '嗡嗡',
                  '我们', '呜呼', '乌乎', '无论', '无宁', '沿着', '毋宁', '向着', '照着', '怎么', '咱们', '在下', '再说', '再者', '怎样', '这边', '这儿',
                  '这个', '这里', '这么', '这时', '这些', '这样', '正如', '之类', '之一', '只是', '只限', '只要', '只有', '至于', '诸位', '着呢', '纵令',
                  '纵然', '纵使', '遵照', '作为', '喔唷', '自从', '自己', '自家', '自身', '总之', '要不', '哎呀', '哎哟', '俺们', '按照', '吧哒', '罢了',
                  '本着', '比方', '比如', '鄙人', '彼此', '别的', '别说', '并且', '不比', '不成', '不单', '不但', '不独', '不管', '不光', '不过', '不仅',
                  '不拘', '不论', '不怕', '不然', '不如', '不特', '不惟', '不问', '不只', '朝着', '趁着', '除非', '除了', '此间', '此外', '从而', '但是',
                  '当着', '的话', '等等', '叮咚', '对于', '多少', '而况', '而且', '而是', '而外', '而言', '而已', '尔后', '反之', '非但', '非徒', '否则',
                  '嘎登', '各个', '各位', '各种', '各自', '根据', '故此', '固然', '关于', '果然', '果真', '哈哈', '何处', '何况', '何时', '哼唷', '呼哧',
                  '还是', '还有', '或是', '或者', '极了', '及其', '及至', '即便', '即或', '即令', '即若', '即使', '既然', '既是', '继而', '加之', '假如',
                  '假若', '假使', '鉴于', '几时', '较之', '接着', '结果', '进而', '尽管', '经过', '就是', '可见', '可是', '可以', '况且', '开始', '开外',
                  '来着', '例如', '连同', '两者', '另外', '慢说', '漫说', '每当', '莫若', '某个', '某些', '哪边', '哪儿', '哪个', '哪里', '哪年', '哪怕',
                  '哪天', '哪些', '哪样', '那边', '那儿', '那个', '那里', '那么', '那时', '那些', '那样', '乃至', '宁可', '宁肯', '宁愿', '你们', '啪达',
                  '旁人', '凭借', '其次', '其二', '其他', '其它', '其一', '其余', '其中', '起见', '起见', '岂但', '前后', '前者', '然而', '然后', '然则',
                  '人家', '任何', '任凭', '如此', '如果', '如何', '如其', '如若', '若非', '若是', '上下', '尚且', '设若', '设使', '甚而', '甚么', '甚至',
                  '省得', '时候', '什么', '使得', '是的', '首先', '首先', '其次', '再次', '最后', '您们', '它们', '她们', '他们', '我们', '你是', '您是',
                  '我是', '他是', '她是', '它是', '不是', '你们', '啊哈', '啊呀', '啊哟', '挨次', '挨个', '挨着', '哎呀', '哎哟', '俺们', '按理', '按期',
                  '默然', '按时', '按说', '按照', '暗中', '暗自', '昂然', '八成', '倍感', '倍加', '本人', '本身', '本着', '并非', '别人', '必定', '比起',
                  '比如', '比照', '鄙人', '毕竟', '必将', '必须', '并肩', '并没', '并排', '并且', '并无', '勃然', '不必', '不常', '不大', '不单', '不但',
                  '而且', '不得', '不迭', '不定', '不独', '不对', '不妨', '不管', '不光', '不过', '不会', '不仅', '不拘', '不力', '不了', '不料', '不论',
                  '不满', '不免', '不起', '不巧', '不然', '不日', '不少', '不胜', '不时', '不是', '不同', '不能', '不要', '不外', '不下', '不限', '不消',
                  '不已', '不再', '不曾', '不止', '不只', '才能', '彻夜', '趁便', '趁机', '趁热', '趁势', '趁早', '趁着', '成心', '乘机', '乘势', '乘隙',
                  '乘虚', '诚然', '迟早', '充分', '出来', '出去', '除此', '除非', '除开', '除了', '除去', '除却', '除外', '处处', '传说', '传闻', '纯粹',
                  '此后', '此间', '此外', '此中', '次第', '匆匆', '从不', '从此', '从而', '从宽', '从来', '从轻', '从速', '从头', '从未', '从小', '从新',
                  '从严', '从优', '从中', '从重', '凑巧', '存心', '达旦', '打从', '大大', '大抵', '大都', '大多', '大凡', '大概', '大家', '大举', '大略',
                  '大约', '大致', '待到', '单纯', '单单', '但是', '但愿', '当场', '当儿', '当即', '当然', '当庭', '当头', '当下', '当真', '当中', '当着',
                  '倒是', '到处', '到底', '到头', '得起', '的话', '的确', '等到', '等等', '顶多', '动辄', '陡然', '独自', '断然', '对于', '顿时', '多次',
                  '多多', '多亏', '而后', '而论', '而且', '而是', '而外', '而言', '而已', '而又', '尔等', '反倒', '反而', '反手', '反之', '方才', '方能',
                  '非常', '非但', '非得', '分头', '奋勇', '愤然', '更为', '更加', '根据', '个人', '各式', '刚才', '敢情', '该当', '嘎嘎', '否则', '赶快',
                  '敢于', '刚好', '刚巧', '高低', '格外', '隔日', '隔夜', '公然', '过于', '果然', '果真', '光是', '关于', '共总', '姑且', '故此', '故而',
                  '故意', '固然', '惯常', '毫不', '毫无', '很多', '何须', '好在', '何必', '何尝', '何妨', '何苦', '何况', '何止', '很少', '轰然', '后来',
                  '呼啦', '哗啦', '互相', '忽地', '忽然', '话说', '或是', '伙同', '豁然', '恍然', '还是', '或许', '或者', '基本', '基于', '极大', '极度',
                  '极端', '极力', '极其', '极为', '即便', '即将', '及其', '及至', '即刻', '即令', '即使', '几度', '几番', '几乎', '几经', '既然', '继而',
                  '继之', '加上', '加以', '加之', '假如', '假若', '假使', '间或', '将才', '简直', '鉴于', '将近', '将要', '交口', '较比', '较为', '较之',
                  '皆可', '截然', '截至', '藉以', '借此', '借以', '届时', '尽快', '近来', '进而', '进来', '进去', '尽管', '尽量', '尽然', '就算', '居然',
                  '就此', '就地', '竟然', '究竟', '经常', '尽早', '精光', '经过', '就是', '局外', '举凡', '据称', '据此', '据实', '据说', '可好', '看来',
                  '开外', '绝不', '决不', '据悉', '决非', '绝顶', '绝对', '绝非', '可见', '可能', '可是', '可以', '恐怕', '来讲', '来看', '快要', '况且',
                  '拦腰', '牢牢', '老是', '累次', '累年', '理当', '理该', '理应', '例如', '立地', '立刻', '立马', '立时', '联袂', '连连', '连日', '路经',
                  '临到', '连声', '连同', '连袂', '另外', '另行', '屡次', '屡屡', '缕缕', '率尔', '率然', '略加', '略微', '略为', '论说', '马上', '猛然',
                  '没有', '每当', '每逢', '每每', '莫不', '莫非', '莫如', '莫若', '哪怕', '那么', '那末', '那些', '乃至', '难道', '难得', '难怪', '难说',
                  '你们', '凝神', '宁可', '宁肯', '宁愿', '偶而', '偶尔', '碰巧', '譬如', '偏偏', '平素', '迫于', '扑通', '其次', '其后', '其实', '其它',
                  '起初', '起来', '起首', '起头', '起先', '岂但', '岂非', '岂止', '恰逢', '恰好', '恰恰', '恰巧', '恰如', '恰似', '前后', '前者', '切莫',
                  '切切', '切勿', '亲口', '亲身', '亲手', '亲眼', '亲自', '顷刻', '请勿', '取道', '权时', '全都', '全力', '全年', '全然', '然而', '然后',
                  '人家', '人人', '仍旧', '仍然', '日见', '日渐', '日益', '日臻', '如常', '如次', '如果', '如今', '如期', '如若', '如上', '如下', '上来',
                  '上去', '瑟瑟', '沙沙', '啊', '哎', '唉', '俺', '按', '吧', '把', '甭', '别', '嘿', '很', '乎', '会', '或', '既', '及', '啦',
                  '了', '们', '你', '您', '哦', '砰', '啊', '你', '我', '他', '她', '它',
                  '第一章','第二章','第三章','第四章','第五章','第六章','第七章','第八章','第九章','第十章',
                  '第十一章','第十二章','第十三章','第十四章','第十五章','第十六章','第十七章','第十八章','第十九章','第二十章'
                  '一','二','三','四','五','六','七','八','九','十','十一'}


class Store:
    database: str

    def __init__(self, db_path):
        self.engine = create_engine(db_path, pool_size=20)
        self.init_tables()
        self.session = self.init_session()
        self.init_tables()
        self.collection_overall = pymongo.MongoClient()['bookstore']['books_info_overall']
        self.collection_specific = pymongo.MongoClient()['bookstore']['books_info_specific']
        self.init_mongo()

    def init_mongo(self):
        book_db = book.BookDB()
        books = book_db.get_book_info(0,100)
        collection_overall = self.collection_overall
        collection_specific = self.collection_specific

        for b in books:
            book_json = b.__dict__  # 把book对象变成dict类型


            tags_list = book_json.get('tags', [])
            tags_string = ' '.join(tags_list)

            raw_content_0 = book_json.get('content', 'no content')
            raw_content = re.sub('[1-9\W+]', '', raw_content_0)

            jieba_list = []
            for i in jieba.cut(raw_content):
                if i not in stop_words:
                    jieba_list.append(i)
            jieba_content = ' '.join(jieba_list)
            try:
                collection_overall.insert_one({
                    "_id": book_json.get('id'),
                    "title": book_json.get('title', ''),
                    "author": book_json.get('author', ''),
                    "publisher": book_json.get('publisher', ''),
                    "original_title": book_json.get("original_title", ''),
                    "translator": book_json.get("translator", ''),
                    "pub_year": book_json.get("pub_year", ''),
                    "pages": book_json.get('pages', 0),
                    "price": book_json.get('price', 0),
                    'currency_unit' : book_json.get('currency_unit', ''),
                    "binding": book_json.get("binding", ''),
                    "isbn": book_json.get('isbn', ''),
                    "author_intro": book_json.get("author_intro", ''),
                    "book_intro": book_json.get("book_intro", ''),
                    "content": raw_content,
                    'jieba_content': jieba_content,
                    'tags': tags_string,
                    'pictures': book_json.get('pictures', [])

                })
            except:
                pass
            try:
                collection_specific.insert_one({
                    "_id": book_json.get('id'),
                    "title": book_json.get('title', ''),
                    "author": book_json.get('author', ''),
                    "publisher": book_json.get('publisher', ''),
                    "original_title": book_json.get("original_title", ''),
                    "translator": book_json.get("translator", ''),
                    "pub_year": book_json.get("pub_year", ''),
                    "pages": book_json.get('pages', 0),
                    "price": book_json.get('price', 0),
                    'currency_unit': book_json.get('currency_unit', ''),
                    "binding": book_json.get("binding", ''),
                    "isbn": book_json.get('isbn', ''),
                    "author_intro": book_json.get("author_intro", ''),
                    "book_intro": book_json.get("book_intro", ''),
                    "content": raw_content,
                    'jieba_content': jieba_content,
                    'tags': tags_list,
                    'pictures': book_json.get('pictures', [])

                })
            except:
                pass

        # collection_overall.create_index([("$**", pymongo.TEXT)])
        collection_overall.create_index([("title",pymongo.TEXT),("author",pymongo.TEXT),("publisher",pymongo.TEXT),("translator",pymongo.TEXT),("author_intro",pymongo.TEXT),("book_intro",pymongo.TEXT),("jieba_content",pymongo.TEXT),("tags",pymongo.TEXT)])
        collection_specific.create_index([("tags", 1)])
        collection_specific.create_index([("title", 1)])
        collection_specific.create_index([("author", 1)])
        collection_specific.create_index([("publisher", 1)])
        # collection_specific.create_index({"jieba_content":pymongo.TEXT})
        collection_specific.create_index([("jieba_content", pymongo.TEXT)])

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            trans = conn.begin()
            conn.execute(

                """
                create table IF NOT EXISTS user(
                user_id varchar(80) not null,
                password varchar(80) not null,
                balance float default 0,
                token longtext default null,
                terminal varchar(80) default null,
                PRIMARY KEY (user_id)
                );
                """

            )
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS book( "
            #     "book_id CHAR(80) PRIMARY KEY, title TEXT, author TEXT, publisher TEXT, "
            #     "original_title TEXT,translator TEXT,pub_year TEXT,pages INTEGER,price INTEGER,"
            #     "currency_unit TEXT,binding TEXT,isbn TEXT,author_intro TEXT,book_intro TEXT,"
            #     "content TEXT,tags TEXT,picture BLOB);"
            # )

            conn.execute(
                """
                create table IF NOT EXISTS store_book(
                store_id varchar(80) not null,
                book_id varchar(80) not null,
                price int default 0,
                stock_level int default 0,
                primary key (store_id, book_id)
                );
                """
                )

            conn.execute(
               """
                create table IF NOT EXISTS user_store(
                store_id varchar(80) not null,
                user_id varchar(80) not null,
                address_from varchar(80),
                primary key (store_id),
                constraint fk_user_id foreign key (user_id) references user(user_id) on delete cascade on update cascade
                );
                """
               )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order("
                "book_id CHAR(80), order_id CHAR(180),count INTEGER,status integer,"
                "PRIMARY KEY(book_id,order_id));"
            )

            conn.execute(
               """
                create table IF NOT EXISTS order_list(
                order_id varchar(180) not null,
                user_id varchar(80) not null,
                store_id varchar(80) not null,
                total_price float default 0,
                time datetime not null,
                address_to varchar(80) default null,
                primary key (order_id),
                constraint fk_user_id_ol foreign key (user_id) references user(user_id) on delete cascade on update cascade,
                constraint fk_store_id_ol foreign key (store_id) references user_store(store_id) on delete cascade on update cascade
                );
               """)

            trans.commit()
        except KeyError as e:
            logging.error(e)
            trans.rollback()

    def get_db_conn(self):
        return self.engine.connect()

    def init_session(self):
        # DBSession = sessionmaker(bind=self.engine)
        # session = DBSession()
        session_factory = sessionmaker(bind=self.engine)
        session = scoped_session(session_factory)
        Base.metadata.create_all(self.engine)
        return session

    def get_collection(self):
        return self.books_storage

    def get_session(self):
        return self.session



database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()


def get_session():
    global database_instance
    return database_instance.get_session()