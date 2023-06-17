from django.shortcuts import render
from django.http import JsonResponse
import json
from urllib.parse import unquote
import os
import pymongo
import datetime
from bson import ObjectId

connect_string = f'mongodb://{os.environ.get("MONGO_INITDB_ROOT_USERNAME")}:{os.environ.get("MONGO_INITDB_ROOT_PASSWORD")}@{os.environ.get("DB_HOSTNAME")}/{os.environ.get("MONGO_INITDB_DATABASE")}?retryWrites=true&w=majority'
my_client = pymongo.MongoClient(connect_string)

dbname = my_client[os.environ.get("MONGO_INITDB_DATABASE")]

orders_collection = dbname["orders"]
restaurant_collection = dbname["restaurant_info"]
items_collection = dbname["items"]


def ordersPage(request):
    orders = []

    results = orders_collection.aggregate(
        [
            {
                '$lookup': {
                    'from': 'items', 
                    'localField': 'items.id', 
                    'foreignField': '_id', 
                    'as': 'orderitems'
                }
            },
            {
                '$match': {'payment': {}}
            },
            {
                '$sort': {'time': -1}
            }
        ]
    )

    context = {"orders": results}

    return render(request, 'orders.html', context)


def newOrder(request):
    restaurant_info = restaurant_collection.find()[0]
    context = {"tables": range(restaurant_info["number_of_tables"])}
    return render(request, 'new_order.html', context)


def orderItems(request):
    items = []

    for x in items_collection.find():
        x["id"] = str(x["_id"])
        items.append(x)

    context = {"items": items}
    return render(request, 'items.html', context)


def addOrder(request):
    data = request.GET
    table = data.get("table")
    time = datetime.datetime.fromisoformat(unquote(data.get("time")))
    items = json.loads(unquote(data.get("items")))
    total = 0
    title_strings = [] # The strings that make up the title of the order
    most_expensive = [0, ""] # Our order image will be the most expensive item for now

    items_list = []

    # Dictionary comprehension to get price of all items
    all_items = { x["_id"]: {"price":x["price"], "name":x["name"], "image_url":x["image_url"]} for x in items_collection.find({})}

    # We will write a more efficient algorithm in future,
    # but for now we assume all restaurants have only a few
    # dozen items on their menu, so perfomance will only take
    # negligible hit

    for i in items:
        item_id = i
        quantity = items[i]
        items_list.append({"id": ObjectId(item_id), "quantity": quantity})
        price = all_items[ObjectId(item_id)]["price"]
        total += price * quantity

        # Order Image URL
        if price > most_expensive[0]:
            most_expensive = [price, all_items[ObjectId(item_id)]['image_url']]

        title_strings.append(f"{quantity} x {all_items[ObjectId(item_id)]['name']}")


    order = orders_collection.insert_one(
        {
        "title": " + ".join(title_strings),
        "image_url": most_expensive[1],
        "items": items_list,
        "table": table,
        "time": time,
        "payment": {},
        "total": total,
        "discount": 0
        }
    )

    return JsonResponse({'id':str(order.inserted_id)})


def toInt(num):
    try:
        integer = int(num)
    except Exception as e:
        integer = 0

    return integer

def confirmPayment(request):
    data = request.GET
    # Check if request has confirm-payment param
    # If not, this may be just a page visit
    # so render the html
    if data.get("action") == "confirm-payment":
        order_id = data.get("order_id")
        mpesa = toInt(data.get("mpesa"))
        cash = toInt(data.get("cash"))

        # Validate that there's an order ID and
        # at least one payment method
        if order_id and any([mpesa, cash]):
            total_paid = mpesa + cash
            order_details = orders_collection.find_one({"_id": ObjectId(order_id)})
            total_expected = order_details.get("total")

            if order_details:
                if order_details.get("payment"):
                    return JsonResponse({"status": 1, "message": "Payment was already recorded"})

                if total_paid >= total_expected:
                    orders_collection.update_one(
                        {"_id": ObjectId(order_id)},
                        {"$set": {"payment": {"mpesa": mpesa, "cash": cash}}}
                    )
                    return JsonResponse({"status": 1, "message": "Successfully recorded payment"})
                else:
                    return JsonResponse({"status": 0, "message": f"Payment must at least Ksh{total_expected}"})
            else:
                return JsonResponse({"status": 0, "message": "Order does not exist"})

        else:
            return JsonResponse({"status": 0, "message": "Enter Mpesa or cash payment details"})

    return render(request, "payments.html")


def summary(request):
    paid_orders = orders_collection.aggregate([
      {"$match": {'payment': {"$gt": {}}}},
      { "$group": {
        "_id": {
          "$dateToString": {
            "format": "%Y-%m-%d",
            "date": "$time"
          }
        },
        "total": {"$sum": "$total"}
      }}
    ])

    unpaid_orders = orders_collection.aggregate([
      {"$match": {'payment': {}}},
      { "$group": {
        "_id": {
          "$dateToString": {
            "format": "%Y-%m-%d",
            "date": "$time"
          }
        },
        "total": {"$sum": "$total"}
      }}
    ])

    context = {"aggregates": paid_orders}

    return render(request, "summary.html", context)
