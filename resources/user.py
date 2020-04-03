from main import Resource, api, fields
from models.user import UserModel, users_schema, user_schema

users_namespace = api.namespace('users', description='THis endpoint deals with all operations regarding users')
user_model = api.model('User', {
    "full_name" :fields.String(),
    "email" :fields.String(),
    "password" :fields.String()
})


@users_namespace.route('')
class ItemList(Resource):
    def get(self):
        """Get a list of all users"""
        users = UserModel.fetch_all()
        if users:
            return users_schema.dump(users)
        else:
            return {'message':'please try again later'}, 500



@users_namespace.route('/<int:id>')
class User(Resource):
    def get(self, id):
        ''' Geta a user by id'''
        user = UserModel.fetch_by_id(id)
        if user:
            return user_schema.dump(user)
        else:
            return {'message':'That user does not exist'}, 404
    
    def delete(self, id):
        '''Delete a user based on id'''
        user = UserModel.fetch_by_id(id)
        if user:
            user.delete_from_db()
            return {'message':'user successfully deleted'}, 200
        else:
            return {'message':'THat user does not exist'}, 404

    def put(self, id):
        '''Edit user by id'''
        user = UserModel.fetch_by_id(id)
        if user:
            if u'full_name' in data['full_name']:
                user.full_name = data['full_name']
            user.save_to_db()
        else:
            return {'message':'That user does not exist'}, 404
