from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from database import Database
from bson import ObjectId
import pymongo


app = Flask(__name__)
api = Api(app)

db = Database('Movie_Web')
#user
class LoginResource(Resource):
    def post(self):
        

        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(email, password)

        # Kiểm tra thông tin đăng nhập với cơ sở dữ liệu MongoDB
        user = db.users_collection.find_one({'email': email, 'password': password})

        if user:
            user['_id'] = str(user['_id'])
            response = jsonify(user)
            response.status_code = 200 # or 400 or whatever
            return response
        else:
            return {'message': 'Invalid email or password'}, 401

api.add_resource(LoginResource, '/login')

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        userName = data.get('username')
        role = data.get('role', 'user')
        if not all([email, password, userName]):
            return {"message": "Missing fields"}, 400
        users = db.users_collection.find_one({'email': email})
        print(users)
        if users:  
            return {
                "error": "Email has been registered."
            },409
        else:
            new_user = {
                'email': email,
                'password': password,
                'userName': userName,
                'role': role
            }
            db.users_collection.insert_one(new_user)
            return {"message": "Successfully"} , 200
api.add_resource(RegisterResource, '/register')


class User(Resource):
    def get(self):
        allUser = db.users_collection.find()
        dataUserJson = []

        for data in allUser:
            id = str(data['_id'])  # Convert ObjectId to string
            email = data['email']
            password = data['password']
            userName = data['userName']
            role = data['role']
           

            DataDict = {
                "_id": id,
                "email": email,
                "password": password,
                "userName": userName,
                "role": role,
                
            }

            dataUserJson.append(DataDict)

        response = jsonify(dataUserJson)
        response.status_code = 200 # or 400 or whatever
        return response
    
api.add_resource(User, '/getAllUser')
class DeleteUserResource(Resource):
    def delete(self, user_id):
        # Xác nhận trước khi xóa
        user = db.users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return {"message": "User not found"}, 404

        result = db.users_collection.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count > 0:
            return {"message": "User deleted successfully"}
        else:
            return {"message": "User not found"}, 404

api.add_resource(DeleteUserResource, '/delete/<string:user_id>', methods=["DELETE"])


class UsersPaginationResource(Resource):
    def get(self):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        
        skip = (page - 1) * page_size

        
        allUser = db.users_collection.find().skip(skip).limit(page_size)

        
        dataUserJson = []

        for data in allUser:
            id = str(data['_id']) 
            email = data['email']
            password = data['password']
            userName = data['userName']
            role = data['role']

            DataDict = {
                "_id": id,
                "email": email,
                "password": password,
                "userName": userName,
                "role": role,
            }

            dataUserJson.append(DataDict)

        response = jsonify(dataUserJson)
        print(dataUserJson)
        response.status_code = 200  # or 400 or whatever
        return response

api.add_resource(UsersPaginationResource, '/users/pagination')
#movie
class MovieResource(Resource):
    def get(self):
        allMovie = db.movies_collection.find()
        dataMovieJson = []

        for data in allMovie:
            id = str(data['_id'])  # Convert ObjectId to string
            MovieName = data['MovieName']
            TitleMovie = data['TitleMovie']
            Description = data['Description']
            Duration = data['Duration']
            Language = data['Language']
            ReleaseDate = data['ReleaseDate']
            Country = data['Country']
            Genre = data['Genre']
            PosterMovie = data['PosterMovie']

            DataDict = {
                "_id": id,
                "MovieName": MovieName,
                "TitleMovie": TitleMovie,
                "Description": Description,
                "Duration": Duration,
                "Language": Language,
                "ReleaseDate": ReleaseDate,
                "Country": Country,
                "Genre": Genre,
                "PosterMovie": PosterMovie,
            }

            dataMovieJson.append(DataDict)

        response = jsonify(dataMovieJson)
        response.status_code = 200 # or 400 or whatever
        return response
    def  post(self):
        data = request.json
        print(data)

        required_fields = ['MovieName', 'TitleMovie', 'Description', 'Duration', 'Language', 'ReleaseDate', 'Country', 'Genre', 'PosterMovie']
        for field in required_fields:
            if field not in data:
                return {'message': f'Missing required field: {field}'}, 400

        result = db.movies_collection.insert_one(data)

        inserted_id = str(result.inserted_id)
        return jsonify({
            'status': 'Data was posted to MongoDB',
            'data': {**data, '_id': inserted_id} 
        })
    

api.add_resource(MovieResource, '/movies')

class ControlMovie(Resource):
    def delete(self, item_id):
        print(item_id)
        # Tìm kiếm và xóa item theo ID và trả về nó trước khi xóa
        result = db.movies_collection.delete_one({"_id": ObjectId(item_id)})

        if result.deleted_count > 0:
            return jsonify({'message': 'Item deleted successfully'})
        else:
            response = make_response(jsonify({'error': 'Item not found'}), 404)
            return response
    def put(self, item_id):
        data = request.json
        print(data)
        # Kiểm tra rỗng thông tin cập nhật
        if not data:
            return {'message': 'No data provided to update'}
            
        # Thêm _id vào dữ liệu để phân biệt record
        data['_id'] = ObjectId(item_id)
        
        # Cập nhật record
        result = db.movies_collection.update_one({'_id': data['_id']}, {"$set": data})
        
        # Trả về thông báo sau khi cập nhật thành công hoặc lỗi
        if result.modified_count > 0:
            return {'message':'Item updated successfully'}, 200
        else:
            response = make_response(jsonify({'error': 'Item not found'}), 404)
            return response
api.add_resource(ControlMovie, '/movies/<string:item_id>')
class MovieDetailsResource(Resource):
    def get(self, movie_id):
        result = db.movies_collection.find_one({"_id": ObjectId(movie_id)})
        
        if result:
            result['_id'] = str(result['_id'])
            response = jsonify(result)
            response.status_code = 200
            return response
        else:
            return {"Error": "No such movie available"}, 404

api.add_resource(MovieDetailsResource, "/movie/<string:movie_id>")

class MovieSearch(Resource):
    def post(self, movie_name):
        # Check if movie_name is provided
       
        if movie_name is None :
            return {"Error": "Movie name is required"}, 400

        # Use a regex query to find movies with partial match in MovieName or titleMovie
        regex_query = {
            "$or": [
                {"MovieName": {"$regex": f".*{movie_name}.*", "$options": "i"}},
                {"TitleMovie": {"$regex": f".*{movie_name}.*", "$options": "i"}}
            ]
        }

        results = list(db.movies_collection.find(regex_query))

        if results:
            # Convert ObjectIds to strings in the results
            for result in results:
                result['_id'] = str(result['_id'])

            response = jsonify(results)
            response.status_code = 200
            return response
        else:
            return {"Error": "No matching movies found"}, 404


api.add_resource(MovieSearch, "/movieSearch/<string:movie_name>")

class MovieFilter(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        loaiPhim=data.get('loaiPhim')
        theloaiPhim=data.get('theloaiPhim')
        quocGia=data.get('quocGia')
        nam=data.get('nam')
        thoiLuong=data.get('thoiLuong')
        sapXep=data.get('sapXep')
        print(loaiPhim,theloaiPhim,quocGia,nam,thoiLuong,sapXep)
        query_conditions = []

        if loaiPhim != 'all':
            query_conditions.append({"Type": {"$regex": f".*{loaiPhim}.*", "$options": "i"}})

        if theloaiPhim != 'all':
            query_conditions.append({"Genre": {"$regex": f".*{theloaiPhim}.*", "$options": "i"}})

        if quocGia != 'all':
            query_conditions.append({"Country": {"$regex": f".*{quocGia}.*", "$options": "i"}})

        if nam != 'all':
            query_conditions.append({
                "$expr": {
                    "$eq": [
                        {"$year": {"$toDate": "$ReleaseDate"}},
                        int(nam)
                    ]
                }
            })

        if thoiLuong != 'all':
            duration = int(thoiLuong)
    
    # Bạn có thể sử dụng "$lte" và "$gte" trực tiếp trong query_conditions
            query_conditions.append({
                "Duration": {
                    "$lte": duration,
                    "$gte": duration - 30
                }
            })

        sort_field = "ReleaseDate"
        sort_order = pymongo.DESCENDING 
        if sapXep != 'all':
            sort_field = "ReleaseDate" if sapXep == 'ngayPhatHanh' else sapXep
              # Sắp xếp giảm dần
        else:
            regex_query = {}
        
        
        if query_conditions:
            regex_query = {"$and": query_conditions}
        else:
            regex_query = {}
    # Bạn có thể sắp xếp ngay khi gọi hàm find

        results = list(db.movies_collection.find(regex_query).sort(sort_field, sort_order))

        
        if results:
            # Convert ObjectIds to strings in the results
            for result in results:
                result['_id'] = str(result['_id'])

            response = jsonify(results)
            response.status_code = 200
            return response
        else:
            return {"Error": "No matching movies found"}, 404
api.add_resource(MovieFilter, "/movieFilter")

if __name__ == '__main__':
    app.run()