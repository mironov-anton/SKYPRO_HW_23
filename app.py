import os

from flask import Flask, request
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# с помощью функционального программирования (функций filter, map), итераторов/генераторов сконструировать запрос
def build_query(file, query):
    query_items = query.split("|")
    res = map(lambda v: v.strip(), file)
    for item in query_items:
        split_item = item.split(":")
        cmd = split_item[0]
        if cmd == "filter":
            arg = split_item[1]
            res = filter(lambda v, txt=arg: txt in v, res)
        if cmd == "map":
            arg = int(split_item[1])
            res = map(lambda v, idx=arg: v.split(" ")[idx], res)
        if cmd == "unique":
            res = set(res)
        if cmd == "sort":
            arg = split_item[1]
            if arg == "desc":
                reverse = True
            else:
                reverse = False
            res = sorted(res, reverse=reverse)
        if cmd == "limit":
            arg = int(split_item[1])
            res = list(res)[:arg]

        return res


@app.route("/perform_query")
def perform_query():
    # получить параметры query и file_name из request.args, при ошибке вернуть ошибку 400
    try:
        query = request.args["query"]
        file_name = request.args["file_name"]
    except KeyError:
        raise BadRequest

    # проверить, что файла file_name существует в папке DATA_DIR, при ошибке вернуть ошибку 400
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return BadRequest(description=f"{file_name} was not found")

    # вернуть пользователю сформированный результат
    with open(file_path) as f:
        result = build_query(f, query)
        content = '\n'.join(result)
    return app.response_class(content, content_type="text/plain")
