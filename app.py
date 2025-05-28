import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename

import bcrypt
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 导入MinIO工具模块
from minio_service.minio_utils import (
    upload_file_data_to_minio, 
    get_file_url, 
    get_public_file_url,
    delete_file_from_minio,
    migrate_local_images_to_minio,
    create_bucket_if_not_exists
)

# 导入WebService中间件
from webservice_middleware.webservice_middleware import webservice_support, soap_webservice_support

# 创建 Flask 应用
app = Flask(__name__)

# 设置 Flask session 密钥
app.config['SECRET_KEY'] = 'your_secret_key'  # 请更换成更安全的密钥

# 启用 CORS，允许来自指定来源的请求，并允许带上 cookies
CORS(app, origins="http://localhost:5173", supports_credentials=True)  # 支持携带凭证

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/car_rental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用对象修改追踪

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 导入 Elasticsearch 工具模块
from elasticsearch_utils import search_cars as es_search_cars, create_index_if_not_exists, bulk_index_cars, format_car_data_for_db, generate_insert_sql

# 省份表模型
class Province(db.Model):
    __tablename__ = 'province_info'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    province_id = db.Column(db.String(12))

    def __repr__(self):
        return f'<Province {self.name}>'

# 城市表模型
class City(db.Model):
    __tablename__ = 'city_info'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    city_id = db.Column(db.String(12))
    province_id = db.Column(db.String(12), db.ForeignKey('province_info.province_id'))

    province = db.relationship('Province', backref= db.backref('cities', lazy=True))

    def __repr__(self):
        return f'<City {self.name}>'

# 区域（国家或区）表模型
class Country(db.Model):
    __tablename__ = 'country_info'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    country_id = db.Column(db.String(12))
    city_id = db.Column(db.String(12), db.ForeignKey('city_info.city_id'))

    city = db.relationship('City', backref=db.backref('countries', lazy=True))

    def __repr__(self):
        return f'<Country {self.name}>'

# 用户表模型
class UserInfo(db.Model):
    __tablename__ = 'user_info'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    real_name = db.Column(db.String(20), nullable=True)
    id_type = db.Column(db.Integer, nullable=True)  # 确保这里有 id_type 字段
    id_number = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    register_time = db.Column(db.DateTime, nullable=True)
    driver_license = db.Column(db.String(50), nullable=True)
    license_expire_date = db.Column(db.Date, nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    emergency_phone = db.Column(db.String(20), nullable=True)
    credit_score = db.Column(db.Integer, nullable=True)


# 门店表模型
class Store(db.Model):
    __tablename__ = 'store_info'

    store_id = db.Column(db.Integer, primary_key=True)  # 门店ID
    store_name = db.Column(db.String(100))  # 门店名称
    address = db.Column(db.String(200))  # 地址
    business_hours = db.Column(db.String(100))  # 营业时间
    phone = db.Column(db.String(20))  # 电话
    country_id = db.Column(db.String(12), db.ForeignKey('country_info.country_id'))  # 区县ID

    # 外键关系
    country = db.relationship('Country', backref=db.backref('stores', lazy=True))

# 创建数据库表（确保应用上下文中执行）

def sync_cars_to_db_and_es():
    """将数据库中的车辆数据同步到Elasticsearch。"""
    with app.app_context():
        cars_for_es_indexing = []
        # 1. 创建 Elasticsearch 索引 (如果不存在)
        create_index_if_not_exists('cars')

        # 2. 从数据库查询所有车辆信息
        all_cars_from_db = CarInfo.query.all()
        if not all_cars_from_db:
            print("No cars found in the database to sync.")
            # 如果数据库没有数据，需要先通过其他方式添加车辆数据到数据库
            # 这里我们假设数据库应该有数据，如果没有则不进行同步
            return

        print(f"Found {len(all_cars_from_db)} cars in the database to sync to Elasticsearch.")

        for db_car in all_cars_from_db:
            # 3. 准备用于 Elasticsearch 的数据
            # 确保字段名称与数据库表结构一致
            
            # 将数字代码转换为文本描述
            fuel_type_map = {0: '汽油', 1: '柴油', 2: '电动', 3: '混合动力', 4: '混动'}
            transmission_map = {0: '自动', 1: '手动', 2: '自动'}
            
            fuel_type_text = fuel_type_map.get(db_car.fuel_type, '未知')
            transmission_text = transmission_map.get(db_car.transmission_type, '未知')
            
            es_car_data = {
                'id': db_car.car_id, # 使用数据库的 car_id 作为 ES 的 id
                'name': f"{db_car.brand} {db_car.model}", # 组合品牌和型号作为车辆名称
                'brand': db_car.brand,
                'model': db_car.model,
                'seats': 5, # 默认5座，如果有car_type关联可以从那里获取
                'fuel_type': fuel_type_text,
                'transmission': transmission_text,
                'price_per_day': 300, # 默认价格，如果有car_type关联可以从那里获取
                'image_url': db_car.car_images, # 直接使用数据库中的 car_images 字段
                'description': f"{db_car.brand} {db_car.model} 是一款{fuel_type_text}车，配备{transmission_text}变速箱。",
                'availability': db_car.rental_status == 0,  # rental_status 0 表示可用
                'color': db_car.color,
                'mileage': db_car.mileage,
                'car_number': db_car.car_number, # 车牌号
                'engine_capacity': db_car.engine_capacity, # 排量
                'gps_device': db_car.gps_device, # GPS设备
                'last_maintain_time': db_car.last_maintain_time.isoformat() if db_car.last_maintain_time else None,
                'next_maintain_mileage': db_car.next_maintain_mileage,
                'buy_time': db_car.buy_time.isoformat() if db_car.buy_time else None,
                'car_condition': db_car.car_condition,
            }
            cars_for_es_indexing.append(es_car_data)

        # 4. 批量索引到 Elasticsearch
        if cars_for_es_indexing:
            bulk_index_cars('cars', cars_for_es_indexing)
            print(f"Successfully indexed {len(cars_for_es_indexing)} cars to Elasticsearch.")
        else:
            print("No cars to index to Elasticsearch based on current DB content.")

# 车辆信息表模型 (需要确保在 sync_cars_to_db_and_es 之前定义)
class CarInfo(db.Model):
    __tablename__ = 'car_info'

    car_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('car_type_info.type_id'), nullable=True)
    car_number = db.Column(db.String(20), nullable=False, unique=True)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    color = db.Column(db.String(20))
    buy_time = db.Column(db.Date)
    mileage = db.Column(db.Integer)
    rental_status = db.Column(db.SmallInteger) # 使用 SmallInteger 替代 tinyint
    car_condition = db.Column(db.SmallInteger)
    transmission_type = db.Column(db.SmallInteger)
    fuel_type = db.Column(db.SmallInteger)
    engine_capacity = db.Column(db.String(20))
    gps_device = db.Column(db.String(50))
    last_maintain_time = db.Column(db.Date)
    next_maintain_mileage = db.Column(db.Integer)
    car_images = db.Column(db.String(1000)) # 存储图片路径或MinIO的key

    # 如果有 car_type_info 表，可以建立关系
    # car_type = db.relationship('CarTypeInfo', backref=db.backref('cars', lazy=True))

# 车辆类型信息表模型 (如果需要关联)
class CarTypeInfo(db.Model):
    __tablename__ = 'car_type_info'
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False)
    seat_num = db.Column(db.Integer)

    price_per_day = db.Column(db.Numeric(10, 2)) # 使用 Numeric 对应 decimal

# 数据库和服务初始化将在主程序启动时执行

# 新的WebService支持路由
@app.route('/api/search_cars', methods=['GET'])
@webservice_support
def api_search_cars():
    query = request.args.get('q', '')
    
    # 如果查询为空，返回所有车辆；否则进行搜索
    if not query.strip():
        # 返回所有车辆 - 使用通配符查询
        results = es_search_cars(query_string='*', index_name='cars')
    else:
        results = es_search_cars(query_string=query, index_name='cars')
    
    # 为每个结果生成MinIO图片URL
    for car in results:
        if car.get('image_url'):
            # 如果image_url是MinIO对象名称，生成访问URL
            if not car['image_url'].startswith('http'):
                car['image_url'] = get_public_file_url(car['image_url'])
    
    return jsonify(results)


# 新的WebService支持路由
@app.route('/api/upload_car_image', methods=['POST'])
@webservice_support
def upload_car_image():
    """上传车辆图片到MinIO"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # 上传文件到MinIO
        object_name = upload_file_data_to_minio(file.stream, file.filename)
        if object_name:
            # 生成访问URL
            file_url = get_public_file_url(object_name)
            return jsonify({
                'success': True,
                'object_name': object_name,
                'file_url': file_url
            })
        else:
            return jsonify({'error': 'Failed to upload file'}), 500
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# 新的WebService支持路由
@app.route('/api/get_image_url/<path:object_name>', methods=['GET'])
@webservice_support
def get_image_url(object_name):
    """获取MinIO中图片的访问URL"""
    try:
        # 获取预签名URL（1小时有效期）
        url = get_file_url(object_name)
        if url:
            return jsonify({'url': url})
        else:
            return jsonify({'error': 'Failed to generate URL'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to get URL: {str(e)}'}), 500


# 新的WebService支持路由
@app.route('/api/update_car_image', methods=['POST'])
@webservice_support
def update_car_image():
    """更新车辆图片"""
    data = request.json
    car_id = data.get('car_id')
    new_image_object_name = data.get('image_object_name')
    
    if not car_id or not new_image_object_name:
        return jsonify({'error': 'car_id and image_object_name are required'}), 400
    
    try:
        # 查找车辆记录
        car = CarInfo.query.get(car_id)
        if not car:
            return jsonify({'error': 'Car not found'}), 404
        
        # 删除旧图片（如果存在且是MinIO对象）
        old_image = car.car_images
        if old_image and not old_image.startswith('http') and old_image.startswith('cars/'):
            delete_file_from_minio(old_image)
        
        # 更新车辆图片字段
        car.car_images = new_image_object_name
        db.session.commit()
        
        # 重新同步到Elasticsearch
        sync_cars_to_db_and_es()
        
        return jsonify({
            'success': True,
            'message': 'Car image updated successfully',
            'new_image_url': get_public_file_url(new_image_object_name)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update car image: {str(e)}'}), 500

@app.route('/api/check_user', methods=['POST'])

@app.route('/api/check_user', methods=['POST'])
def check_user():
    data = request.json
    username = data.get('username')
    phone = data.get('phone')
    email = data.get('email')
    id_number = data.get('id_number')

    # 检查用户名是否已存在
    if UserInfo.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400

    # 检查手机号是否已注册
    if UserInfo.query.filter_by(phone=phone).first():
        return jsonify({'message': '该手机号码已注册'}), 400

    # 检查邮箱是否已注册
    if UserInfo.query.filter_by(email=email).first():
        return jsonify({'message': '该邮箱已注册'}), 400

    # 检查身份证号码是否已注册
    if UserInfo.query.filter_by(id_number=id_number).first():
        return jsonify({'message': '该身份证号码已注册'}), 400

    return jsonify({'message': '验证通过'}), 200


# 新的WebService支持路由
@app.route('/api/register_user', methods=['POST'])
@webservice_support
def register_user():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']  # 密码不加密
    real_name = data['real_name']
    phone = data['phone']
    id_number = data['id_number']

    # 检查用户是否已经存在
    if UserInfo.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    if UserInfo.query.filter_by(phone=phone).first():
        return jsonify({'message': '该手机号码已注册'}), 400
    if UserInfo.query.filter_by(email=email).first():
        return jsonify({'message': '该邮箱已注册'}), 400
    if UserInfo.query.filter_by(id_number=id_number).first():
        return jsonify({'message': '该身份证号码已注册'}), 400

    # 获取当前时间作为注册时间
    register_time = datetime.now()

    # 插入新用户到 user_info 表
    new_user = UserInfo(
        username=username,
        email=email,
        password=password,  # 直接存储密码
        real_name=real_name,
        phone=phone,
        id_number=id_number,
        register_time=register_time  # 设置注册时间
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True}), 201


# 新的WebService支持路由
@app.route('/api/login', methods=['POST'])
@webservice_support
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 查找用户
    user = UserInfo.query.filter_by(username=username).first()

    if user:
        # 直接比较密码（明文密码对比）
        if password == user.password:
            # 密码正确，设置 session
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['email'] = user.email

            # 登录成功，返回响应
            response = jsonify({
                "message": "登录成功",
                "status": "success",
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email
                }
            })

            # 这里不再需要手动设置 session.sid
            # response.set_cookie('session', session.sid, secure=True, samesite='None', httponly=True)

            # 返回响应
            return response, 200
        else:
            # 密码错误
            return jsonify({"message": "密码错误，请检查您的密码", "status": "error"}), 400
    else:
        # 用户不存在
        return jsonify({"message": "该用户不存在，请检查用户名", "status": "error"}), 404


# 新的WebService支持路由
@app.route('/api/get_user_info', methods=['GET'])
@webservice_support
def get_user_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "未登录，用户ID为空", "status": "error"}), 401

    user = UserInfo.query.filter_by(user_id=user_id).first()
    if user:
        return jsonify({
            "status": "success",
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "real_name": user.real_name,
                "id_type": user.id_type,
                "id_number": user.id_number,
                "phone": user.phone,
                "register_time": user.register_time.strftime('%Y-%m-%d %H:%M:%S') if user.register_time else None
            }
        })
    else:
        return jsonify({"message": "用户不存在", "status": "error"}), 404


# 新的WebService支持路由
@app.route('/api/update_user_info', methods=['PUT'])
@webservice_support
def update_user_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "未登录", "status": "error"}), 401

    user = UserInfo.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "用户不存在", "status": "error"}), 404

    data = request.get_json()

    # 检查用户名是否被其他用户使用
    if data.get('username') and data['username'] != user.username:
        existing_user = UserInfo.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.user_id != user_id:
            return jsonify({"message": "用户名已被使用", "status": "error"}), 400

    # 检查邮箱是否被其他用户使用
    if data.get('email') and data['email'] != user.email:
        existing_user = UserInfo.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.user_id != user_id:
            return jsonify({"message": "邮箱已被使用", "status": "error"}), 400

    # 检查手机号是否被其他用户使用
    if data.get('phone') and data['phone'] != user.phone:
        existing_user = UserInfo.query.filter_by(phone=data['phone']).first()
        if existing_user and existing_user.user_id != user_id:
            return jsonify({"message": "手机号已被使用", "status": "error"}), 400

    # 更新用户信息
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "用户信息更新成功"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "更新失败：" + str(e)
        }), 500


# 新的WebService支持路由
@app.route('/api/logout', methods=['POST'])
@webservice_support
def logout():
    session.clear()
    return jsonify({
        "status": "success",
        "message": "已成功退出登录"
    })


# 省份接口
@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    provinces = Province.query.all()  # 获取所有省份
    province_list = [{"label": province.name, "value": province.province_id} for province in provinces]
    response = jsonify({
        "provinces": province_list
    })
    response.set_data(json.dumps(response.get_json(), ensure_ascii=False))
    return response

# 获取某省所有城市
@app.route('/api/cities', methods=['GET'])
def get_cities():
    province_id = request.args.get('province_id')
    if not province_id:
        return jsonify({"error": "省份 ID 参数不能为空"}), 400

    cities = City.query.filter_by(province_id=province_id).all()
    city_list = [{"label": city.name, "value": city.city_id} for city in cities]

    response = jsonify({"cities": city_list})
    response.set_data(json.dumps(response.get_json(), ensure_ascii=False))
    return response

# 获取某城市所有区域（国家或区）
@app.route('/api/countries', methods=['GET'])
def get_countries():
    city_id = request.args.get('city_id')
    if not city_id:
        return jsonify({"error": "城市 ID 参数不能为空"}), 400

    countries = Country.query.filter_by(city_id=city_id).all()
    country_list = [{"label": country.name, "value": country.country_id} for country in countries]

    response = jsonify({"countries": country_list})
    response.set_data(json.dumps(response.get_json(), ensure_ascii=False))
    return jsonify({"countries": country_list})

# 获取某城市所有门店
@app.route('/api/stores', methods=['GET'])
def get_stores():
    country_id = request.args.get('country_id')
    if not country_id:
        return jsonify({"error": "区县 ID 参数不能为空"}), 400

    stores = Store.query.filter_by(country_id=country_id).all()
    store_list = [{"store_id": store.store_id,
                   "store_name": store.store_name,
                   "address": store.address,
                   "business_hours": store.business_hours,
                   "phone": store.phone} for store in stores]

    return jsonify({"stores": store_list})

@app.route('/api/city-tree', methods=['GET'])
def get_city_tree():
    try:
        # 获取所有省份及其关联数据
        provinces = Province.query.all()
        
        # 构建树状结构数据
        tree_data = []
        for province in provinces:
            province_data = {
                'id': province._id,
                'name': province.name,
                'code': province.province_id,
                'cities': []
            }
            
            # 获取该省份的所有城市
            cities = City.query.filter_by(province_id=province.province_id).all()
            for city in cities:
                city_data = {
                    'id': city._id,
                    'name': city.name,
                    'code': city.city_id,
                    'districts': []
                }
                
                # 获取该城市的所有区县
                countries = Country.query.filter_by(city_id=city.city_id).all()
                city_data['districts'] = [{
                    'id': country._id,
                    'name': country.name,
                    'code': country.country_id
                } for country in countries]
                
                province_data['cities'].append(city_data)
            
            tree_data.append(province_data)
        
        return jsonify(tree_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hot-cities', methods=['GET'])
def get_hot_cities():
    try:
        # 从 city_info 表获取城市数据
        cities = City.query.join(Province, City.province_id == Province.province_id)\
                         .add_columns(City.name.label('city_name'),
                                    City.city_id,
                                    Province.name.label('province_name'))\
                         .limit(18).all()  # 限制返回18个城市
        
        city_list = [{
            'city_id': city.city_id,
            'city_name': city.city_name,
            'province_name': city.province_name
        } for city in cities]
        
        return jsonify({
            'status': 'success',
            'cities': city_list
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 初始化MinIO存储桶
        print("Initializing MinIO...")
        create_bucket_if_not_exists()
        
        # 迁移本地图片到MinIO（仅在首次运行时）
        local_images_path = os.path.join('car-rental', 'src', 'assets', 'images')
        if os.path.exists(local_images_path):
            print("Migrating local images to MinIO...")
            migration_map = migrate_local_images_to_minio(local_images_path)
            print(f"Migrated {len(migration_map)} images to MinIO")
        
        # 创建Elasticsearch索引
        create_index_if_not_exists()
        
        # 在应用启动时执行一次数据同步
        # 注意：这仅为演示目的，实际生产环境中，数据同步策略会更复杂
        # 例如，通过管理命令、定时任务或在数据发生变更时触发同步
        if not CarInfo.query.first(): # 简单判断，如果car_info表为空，则执行同步
            print("Car_info table is empty. Attempting to sync data...")
            print("Attempting to sync data from DB to ES during startup...")
            sync_cars_to_db_and_es() # 总是尝试在启动时同步，以确保ES最新
        else:
            print("Car_info table already contains data. Forcing sync for development.")
            sync_cars_to_db_and_es()
    
    app.run(debug=True)
