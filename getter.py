import json


def getDb():
    with open('db.json', 'r',encoding='utf-8') as file:
        return json.load(file)


def update(db):
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(db, file, indent=4, ensure_ascii=False)