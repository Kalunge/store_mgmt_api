from main import db, api, fields, Resource, jwt_required, get_jwt_identity
from models.store import StoreModel, stores_scehma, store_schema
from models.user import UserModel

store_namespace = api.namespace(
    "stores", description="This Endpoint deals with all operations pertaining Stores"
)

store_model = api.model("Store", {"name": fields.String()})
STORE_NOT_FOUND = "that store does not exists"
OPERATION_SUCCESSFUL = " '{}' operation carried out successfully"


@store_namespace.route("")
class StoreList(Resource):
    @jwt_required
    @api.doc(security="apikey")
    def get(self):
        """Get a list of stores"""
        user_id = get_jwt_identity()
        user = UserModel.fetch_by_id(user_id)
        stores = user.stores
        if stores:
            return stores_scehma.dump(stores), 200
        else:
            return {"message": STORE_NOT_FOUND}, 404

    @api.expect(store_model)
    @jwt_required
    @api.doc(security="apikey")
    def post(self):
        """create a new store"""
        data = api.payload
        name = data["name"]
        user_id = get_jwt_identity()
        store = StoreModel.fetch_by_name(name)
        if store:
            return {"message": "a store by that name already exists"}, 400
        else:
            store = StoreModel(**data, user_id=user_id)
            store.save_to_db()

            return store_schema.dump(store)


@store_namespace.route("/<int:id>")
class Store(Resource):
    @jwt_required
    @api.doc(security="apikey")
    def get(self, id: int):
        """Get a store by its id"""
        store = StoreModel.fetch_by_id(id)
        if store:
            return store_schema.dump(store), 200
        else:
            return {"message": STORE_NOT_FOUND}, 404

    @jwt_required
    @api.doc(security="apikey")
    def delete(self, id: int):
        """DElete a store by id"""
        store = StoreModel.fetch_by_id(id)
        if store:
            store.delete_from_db()
            return {"message": OPERATION_SUCCESSFUL.format("Delete")}
        else:
            return {"message": STORE_NOT_FOUND}, 404

    @api.expect(store_model)
    @jwt_required
    @api.doc(security="apikey")
    def put(self, id: int):
        """edit a store based on its id"""
        data = api.payload
        store = StoreModel.fetch_by_id(id)
        if store:
            if u"name" in data["name"]:
                store.name = name
            return {"message": OPERATION_SUCCESSFUL.format("update")}, 201
        else:
            return {"message": STORE_NOT_FOUND}, 404
