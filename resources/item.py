from main import (
    db,
    Resource,
    api,
    fields,
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
    jwt_optional,
    fresh_jwt_required,
)
from models.item import ItemModel, items_schema, item_schema
from models.user import UserModel
from typing import List, Dict, Union

ITEM_NOT_FOUND = "That item does not exist"
ALREADY_EXISTS = "an item with that name already exists"
OPERATION_SUCCESSFUL = " z{} operation successful"

item_namespace = api.namespace(
    "items", description="This endpoint deals with opertaions concerning Items"
)
item_model = api.model(
    "Item",
    {"name": fields.String(), "price": fields.Float(), "store_id": fields.Integer()},
)


@item_namespace.route("")
class ItemList(Resource):
    @jwt_optional
    @api.doc(security="apikey")
    def get(self):
        """Get aa list of all items"""
        user_id = get_jwt_identity()
        if user_id:
            user = UserModel.fetch_by_id(user_id)
            items = user.items
            return items_schema.dump(items)
        else:
            items = ItemModel.fetch_all()
            return (
                {
                    "item": [item.name for item in items],
                    "message": "Login to view more items",
                },
                200,
            )

    @api.expect(item_model)
    @jwt_required
    @api.doc(security="apikey")
    def post(self):
        """create an item"""
        data = api.payload
        if ItemModel.find_by_name(data["name"]):
            return {"message": ALREADY_EXISTS}, 400
        user_id = get_jwt_identity()
        item = ItemModel(**data, user_id=user_id)
        item.save_to_db()
        return item_schema.dump(item), 201


@item_namespace.route("/<int:id>")
class Item(Resource):
    @jwt_required
    @api.doc(security="apikey")
    def get(self, id: int):
        """get an item based on its id"""
        item = ItemModel.find_by_id(id)
        if item:
            return item_schema.dump(item), 200
        else:
            return {"message": ITEM_NOT_FOUND}, 404

    @jwt_required
    @api.doc(security="apikey")
    def delete(self, id: int):
        claims = get_jwt_claims()
        if not claims:
            return {"message": "Admin privileges required"}
        """DElete an item based on its id"""
        item = ItemModel.find_by_id(id)
        if item:
            item.delete_from_db()
            return {"message": OPERATION_SUCCESSFUL.format("delete")}, 200
        else:
            return {"message": ITEM_NOT_FOUND}, 404

    @api.expect(item_model)
    @fresh_jwt_required
    @api.doc(security="apikey")
    def put(self, id: int):
        """Edit an item by its id """
        data = api.payload
        item = ItemModel.find_by_id(id)
        if item:
            if u"price" in data:
                item.price = data["price"]
            if u"name" in data:
                item.name = data["name"]
            item.save_to_db()
            return item_schema.dump(item)
        else:
            return {"message": ITEM_NOT_FOUND}, 404
