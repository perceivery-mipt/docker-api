from fastapi import FastAPI, Request, HTTPException, responses
from fastapi.responses import JSONResponse, Response
from scalar_doc import ScalarConfiguration, ScalarDoc
from xml.etree.ElementTree import Element, SubElement, tostring
import pandas as pd
import datetime

DESCRIPTION = """
# Автодокументация API

## Раздел 1. Общая информация
Данный сервер реализует API для работы со списком товаров.

## Раздел 2. Возможности API
Сервер поддерживает:
- получение списка товаров;
- получение товара по идентификатору;
- добавление нового товара;
- возврат ответа в форматах JSON и XML.

## Раздел 3. Назначение сервера
API разработан для демонстрациии подхода code-first,
автодокументации OpenAPI и тестирования через Scalar.
"""

tags_metadata = [
    {
        "name": "service",
        "description": "Служебные маршруты для проверки работоспособности API."
    },
    {
        "name": "items",
        "description": "Операции с товарами: получение списка, получение по идентификатору и создание новых записей."
    },
    {
        "name": "test",
        "description": "Тестовый маршрут для проверки работы POST-запроса через Scalar."
    }
]

app = FastAPI(
    title="HW1. Проектирование API",
    description=DESCRIPTION,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=None,
    redoc_url=None
)

docs = ScalarDoc.from_spec(spec=app.openapi_url, mode="url")
docs.set_title("Автодокументация API")
docs.set_configuration(ScalarConfiguration())

# данные
df = pd.DataFrame([
    ['Антифриз EURO G11 (-45°С) зеленый, силикатный 5кг', 1025, 329, 11, 'c', 'антифриз', datetime.datetime(2026, 10, 16, 12, 36, 22)],
    ['Антифриз готовый фиолетовый Синтек MULTIFREEZE 5кг', 250, 315, 38, 'b', 'антифриз', datetime.datetime(2025, 12, 11, 8, 25, 31)],
    ['Антифриз G11 зеленый', 120, 329, 61, 'b', 'антифриз', datetime.datetime(2025, 6, 15, 15, 36, 30)],
    ['Антифриз Antifreeze OEM China OAT red -40 5кг', 390, 504, 65, 'c', 'антифриз', datetime.datetime(2025, 11, 30, 4, 12, 39)],
    ['Антифриз G11 зеленый', 135, 407, 93, 'b', 'антифриз', datetime.datetime(2026, 8, 25, 3, 24, 1)],
], columns=['Наименование товара', 'Цена, руб.', 'cpm', 'Скидка', 'tp', 'Категория', 'dt'])

df['Год'] = df['dt'].dt.year
df = df.drop(['cpm', 'tp', 'dt'], axis=1)

items_db = {
    str(i + 1): row
    for i, row in enumerate(df.to_dict(orient='records'))
}
next_id = len(items_db) + 1

# xml чтение
def dict_to_xml(tag, data):
    root = Element(tag)
    for key, value in data.items():
        child = SubElement(root, str(key))
        child.text = str(value)
    return tostring(root, encoding="utf-8", xml_declaration=True)

def list_to_xml(root_tag, item_tag, data_list):
    root = Element(root_tag)
    for row in data_list:
        item = SubElement(root, item_tag)
        for key, value in row.items():
            child = SubElement(item, str(key))
            child.text = str(value)
    return tostring(root, encoding="utf-8", xml_declaration=True)

# ручки
@app.get("/", tags=["service"], summary="Проверка состояния API")
def root():
    return {"message": "API is running"}

@app.get("/items", tags=["items"], summary="Получение списка товаров")
def get_items(request: Request):
    accept = request.headers.get("accept", "application/json")
    data = list(items_db.values())

    if "application/xml" in accept:
        xml_data = list_to_xml("items", "item", data)
        return Response(content=xml_data, media_type="application/xml")

    return JSONResponse(content=data)

@app.get("/items/{item_id}", tags=["items"], summary="Получение товара по идентификатору")
def get_item(item_id: str, request: Request):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    accept = request.headers.get("accept", "application/json")
    data = items_db[item_id]

    if "application/xml" in accept:
        xml_data = dict_to_xml("item", data)
        return Response(content=xml_data, media_type="application/xml")

    return JSONResponse(content=data)

@app.post("/items", tags=["items"], summary="Создание нового товара")
def create_item(item: dict):
    global next_id

    item_id = str(next_id)
    items_db[item_id] = item
    next_id += 1

    return JSONResponse(
        status_code=201,
        content={
            "id": item_id,
            "item": item
        }
    )

@app.post("/foo", tags=["test"], summary="Тестовый POST-маршрут")
def post_foo(a: str):
    return a + " - ok"

@app.get("/docs", include_in_schema=False)
def get_docs():
    return responses.HTMLResponse(docs.to_html())

@app.get("/docs2", include_in_schema=False)
def get_docs2():
    docs2 = ScalarDoc.from_spec("http://localhost/openapi.json", mode="url")
    docs2.set_title("Автодокументация")
    docs2.set_configuration(ScalarConfiguration())
    return responses.HTMLResponse(docs2.to_html())