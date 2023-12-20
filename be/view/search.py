from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import store
from be.model.model import StoreBook
from be.model import error
import pymongo

bp_search = Blueprint("search",__name__,url_prefix = "/search")

client = pymongo.MongoClient()
db = client.bookstore
books_storage_overall = db.books_info_overall
books_storage = db.books_info_specific
books_content = db.books_content

size = 6 #每页显示的数据量

@bp_search.route("",methods=["POST"])
def search():
    num_page: int = request.json.get("num_page")
    search_target: str = request.json.get("search_target")  # None表示全局搜索
    overall_keyword: str = request.json.get("overall_keyword")
    title_keyword: str = request.json.get("title_keyword")
    author_keyword: str = request.json.get("author_keyword")
    publisher_keyword: str = request.json.get("publisher_keyword")
    # price: int = request.json.get("pub_year")
    content_keyword: str = request.json.get("content_keyword")
    tag_keyword: str = request.json.get("tag_keyword")

    offset = (num_page - 1) * size
    if overall_keyword is not None:
        if search_target is not None:
            session = store.get_session()
            list_books = session.query(StoreBook.store_id).filter(StoreBook.store_id == search_target).all()
            books = []
            for b in list_books:
                books.append(b[0])
            if len(books)==0:
                code, message = error.error_non_exist_store_id(search_target)
                return jsonify({"message": message}), code
            books_info = list(books_storage_overall.find({'_id':{"$in":books},'$text':{'$search':overall_keyword}},{"$score":{"$meta":"textScore"}}).sort([('$score', {'$meta': 'textScore'})]).limit(size).skip(offset))
        else:
            books_info = list(books_storage_overall.find({'$text':{'$search':overall_keyword}},{"$score":{"$meta":"textScore"}}).sort([('$score', {'$meta': 'textScore'})]).limit(size).skip(offset))
            print(books_info)
        return jsonify({"searched books": books_info}), 200

    keywords = {}
    keyword_list=[]
    if title_keyword is not None:
        keywords['title'] = title_keyword
        keyword_list.append(('title',pymongo.DESCENDING))
    if author_keyword is not None:
        keywords['author'] = author_keyword
        keyword_list.append(('author',pymongo.DESCENDING))
    if publisher_keyword is not None:
        keywords['publisher'] = publisher_keyword
        keyword_list.append(('publisher',pymongo.DESCENDING))
    if content_keyword is not None:
        keywords['content_cut'] = content_keyword
        keyword_list.append(('content_cut',pymongo.DESCENDING))
    if tag_keyword is not None:
        keywords['tag'] = tag_keyword
        keyword_list.append(('tag',pymongo.DESCENDING))

    # offset = (num_page-1)*size
    if search_target is not None:
        session = store.get_session()
        list_books = session.query(StoreBook.store_id).filter(StoreBook.store_id == search_target).all()
        books = []
        for b in list_books:
            books.append(b[0])
        if len(books)==0:
            code, message = error.error_non_exist_store_id(search_target)
            return jsonify({"message": message}), code
        books_info = list(books_storage.find({"$and":[{'_id':{"$in":books}},keywords]}).sort(keyword_list).limit(size).skip(offset))
    else:
        books_info = list(books_storage.find(keywords).sort(keyword_list).limit(size).skip(offset))

    return jsonify({"searched books": books_info}), 200
    



