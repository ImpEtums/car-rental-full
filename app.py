import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import jwt  # 添加JWT库
from functools import wraps  # 添加装饰器支持

import bcrypt
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import redis  # 导入Redis库

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

# JWT 密钥（与 Node.js 后端保持一致）
JWT_SECRET = 'your_very_strong_and_random_jwt_secret_key_here'

# 启用 CORS，允许来自指定来源的请求，并允许带上 cookies
CORS(app, origins=["http://localhost:5173", "http://localhost"], supports_credentials=True)  # 支持携带凭证

# 配置数据库连接 - 从环境变量获取或使用默认值
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'mysql+pymysql://root:123456@localhost/car_rental'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用对象修改追踪

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 初始化Redis连接 - 从环境变量获取或使用默认值
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
if redis_url.startswith('redis://'):
    # 解析redis://host:port/db格式
    redis_parts = redis_url.replace('redis://', '').split('/')
    redis_host_port = redis_parts[0].split(':')
    redis_host = redis_host_port[0]
    redis_port = int(redis_host_port[1]) if len(redis_host_port) > 1 else 6379
    redis_db = int(redis_parts[1]) if len(redis_parts) > 1 else 0
else:
    redis_host = 'localhost'
    redis_port = 6379
    redis_db = 0

redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# 导入 Elasticsearch 工具模块
try:
    from elasticsearch_utils import search_cars as es_search_cars, create_index_if_not_exists, bulk_index_cars, format_car_data_for_db, generate_insert_sql
except ImportError as e:
    print(f"Warning: Elasticsearch utils import failed: {e}")
    # 定义空函数作为fallback
    def create_index_if_not_exists(*args, **kwargs):
        print("Elasticsearch not available")
        pass
    def es_search_cars(*args, **kwargs):
        return []
    def bulk_index_cars(*args, **kwargs):
        pass

# JWT 认证装饰器
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取 token
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': '无效的认证头格式', 'status': 'error'}), 401
        
        if not token:
            return jsonify({'message': '缺少认证 token', 'status': 'error'}), 401
        
        try:
            # 验证 token
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['userId']  # 修改：使用 'userId' 而不是 'id'
            
            # 将用户ID添加到请求上下文中
            request.current_user_id = current_user_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token 已过期', 'status': 'error'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的 token', 'status': 'error'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

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

    province = db.relationship('Province', backref=db.backref('cities', lazy=True))

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
    daily_rent = db.Column(db.Numeric(10, 2))  # 日租金
    deposit = db.Column(db.Numeric(10, 2))  # 押金
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

# 新增MySQL搜索车辆的API
@app.route('/search_cars', methods=['GET'])
@webservice_support
def search_cars_mysql():
    """使用MySQL替代Elasticsearch的车辆搜索"""
    query = request.args.get('q', '').strip()
    
    try:
        if not query:
            # 返回所有可用车辆
            cars_query = db.session.query(CarInfo, CarTypeInfo).join(
                CarTypeInfo, CarInfo.type_id == CarTypeInfo.type_id
            ).filter(CarInfo.rental_status == 0)  # 只返回可租赁的车辆
        else:
            # 使用MySQL LIKE查询进行搜索
            cars_query = db.session.query(CarInfo, CarTypeInfo).join(
                CarTypeInfo, CarInfo.type_id == CarTypeInfo.type_id
            ).filter(
                db.and_(
                    CarInfo.rental_status == 0,  # 只返回可租赁的车辆
                    db.or_(
                        CarInfo.brand.like(f'%{query}%'),
                        CarInfo.model.like(f'%{query}%'),
                        CarTypeInfo.type_name.like(f'%{query}%'),
                        CarInfo.color.like(f'%{query}%')
                    )
                )
            )
        
        cars = cars_query.all()
        
        # 格式化返回数据
        result = []
        for car_info, car_type in cars:
            result.append({
                'car_id': car_info.car_id,
                'brand': car_info.brand,
                'model': car_info.model,
                'color': car_info.color,
                'type_name': car_type.type_name,
                'daily_rent': float(car_type.daily_rent),
                'deposit': float(car_type.deposit),
                'image': car_info.car_images or '/src/assets/images/c1.png',
                'transmission_type': car_info.transmission_type,
                'fuel_type': car_info.fuel_type,
                'engine_capacity': car_info.engine_capacity
            })
        
        return jsonify({
            'status': 'success',
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        print(f"搜索车辆时出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '搜索失败',
            'data': []
        }), 500


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
@app.route('/api/auth/register_user', methods=['POST'])
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
@jwt_required  # 使用 JWT 认证
def get_user_info():
    user_id = request.current_user_id  # 从 JWT token 中获取用户ID
    
    try:
        user = UserInfo.query.filter_by(user_id=user_id).first()
        if user:
            return jsonify({
                "status": "success",
                "user_info": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "real_name": user.real_name,
                    "id_number": user.id_number,
                    "id_type": user.id_type,
                    "register_time": user.register_time.strftime('%Y-%m-%d %H:%M:%S') if user.register_time else None
                }
            })
        else:
            return jsonify({"message": "用户不存在", "status": "error"}), 404
    except Exception as e:
        return jsonify({"message": f"获取用户信息失败: {str(e)}", "status": "error"}), 500


# 新的WebService支持路由
@app.route('/api/update_user_info', methods=['PUT', 'POST'])  # 同时支持 PUT 和 POST
@webservice_support
@jwt_required  # 使用 JWT 认证
def update_user_info():
    user_id = request.current_user_id  # 从 JWT token 中获取用户ID
    
    data = request.get_json()
    
    try:
        user = UserInfo.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({"message": "用户不存在", "status": "error"}), 404
        
        # 检查用户名是否已存在（如果要更新用户名）
        if 'username' in data and data['username'] != user.username:
            existing_user = UserInfo.query.filter_by(username=data['username']).first()
            if existing_user:
                return jsonify({"message": "用户名已存在", "status": "error"}), 400
        
        # 检查邮箱是否已存在（如果要更新邮箱）
        if 'email' in data and data['email'] != user.email:
            existing_email = UserInfo.query.filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({"message": "邮箱已被使用", "status": "error"}), 400
        
        # 检查手机号是否已存在（如果要更新手机号）
        if 'phone' in data and data['phone'] != user.phone:
            existing_phone = UserInfo.query.filter_by(phone=data['phone']).first()
            if existing_phone:
                return jsonify({"message": "手机号已被使用", "status": "error"}), 400
        
        # 检查身份证号是否已存在（如果要更新身份证号）
        if 'id_number' in data and data['id_number'] != user.id_number:
            existing_id = UserInfo.query.filter_by(id_number=data['id_number']).first()
            if existing_id:
                return jsonify({"message": "身份证号已被使用", "status": "error"}), 400
        
        # 更新用户信息
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'real_name' in data:
            user.real_name = data['real_name']
        if 'id_number' in data:
            user.id_number = data['id_number']
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "用户信息更新成功"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"更新失败: {str(e)}"
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
    provinces = Province.query.all()
    province_list = [{"label": province.name, "value": province.province_id} for province in provinces]
    response = jsonify({"provinces": province_list})
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
    return response

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

# 在现有模型定义后添加订单相关模型
class OrderInfo(db.Model):
    __tablename__ = 'order_info'
    
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'), nullable=False)
    car_id = db.Column(db.Integer, nullable=False)
    pickup_store_id = db.Column(db.Integer, nullable=False)
    return_store_id = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    actual_start_time = db.Column(db.DateTime, nullable=True)
    actual_end_time = db.Column(db.DateTime, nullable=True)
    rental_days = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2), nullable=False)
    coupon_id = db.Column(db.Integer, nullable=True)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.SmallInteger, default=0)  # 0-待支付/1-已支付/2-已取车/3-已还车/4-已取消
    
    # 关联用户表
    user = db.relationship('UserInfo', backref=db.backref('orders', lazy=True))

# 添加创建订单的API
@app.route('/api/create_order', methods=['POST'])
@webservice_support
@jwt_required
def create_order():
    user_id = request.current_user_id
    data = request.get_json()
    
    try:
        # 手动生成订单ID（临时解决方案）
        max_order = db.session.query(db.func.max(OrderInfo.order_id)).scalar()
        next_order_id = (max_order or 0) + 1
        
        # 创建新订单
        new_order = OrderInfo(
            order_id=next_order_id,  # 手动设置订单ID
            user_id=user_id,
            car_id=data.get('car_id'),
            pickup_store_id=data.get('pickup_store_id', 301),
            return_store_id=data.get('return_store_id', 302),
            start_time=datetime.fromisoformat(data.get('start_time').replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(data.get('end_time').replace('Z', '+00:00')),
            rental_days=data.get('rental_days'),
            total_amount=data.get('total_amount'),
            deposit=data.get('deposit', 150.00),
            coupon_id=data.get('coupon_id'),
            discount_amount=data.get('discount_amount', 0.00),
            status=1
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "订单创建成功",
            "order_id": new_order.order_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"订单创建失败: {str(e)}"
        }), 500

# 添加获取用户订单的API
@app.route('/api/user_orders', methods=['GET'])
@webservice_support
@jwt_required  # 添加JWT认证装饰器
def get_user_orders():
    user_id = request.current_user_id  # 从JWT token中获取用户ID
    
    try:
        orders = OrderInfo.query.filter_by(user_id=user_id).order_by(OrderInfo.create_time.desc()).all()
        
        order_list = []
        for order in orders:
            # 状态映射
            status_map = {
                0: '待支付',
                1: '已支付',
                2: '已取车',
                3: '已还车',
                4: '已取消'
            }
            
            order_data = {
                'order_id': order.order_id,
                'user_id': order.user_id,
                'car_id': order.car_id,
                'pickup_store_id': order.pickup_store_id,
                'return_store_id': order.return_store_id,
                'order_time': order.order_time.isoformat() if order.order_time else None,
                'start_time': order.start_time.isoformat() if order.start_time else None,
                'end_time': order.end_time.isoformat() if order.end_time else None,
                'actual_start_time': order.actual_start_time.isoformat() if order.actual_start_time else None,
                'actual_end_time': order.actual_end_time.isoformat() if order.actual_end_time else None,
                'rental_days': order.rental_days,
                'total_amount': float(order.total_amount),
                'deposit': float(order.deposit),
                'coupon_id': order.coupon_id,
                'discount_amount': float(order.discount_amount),
                'create_time': order.create_time.isoformat() if order.create_time else None,
                'update_time': order.update_time.isoformat() if order.update_time else None,
                'status': order.status,
                'status_description': status_map.get(order.status, '未知状态'),
                'name': f'订单 {order.order_id:03d}',
                'image': '/assets/images/c1.png'
            }
            order_list.append(order_data)
        
        # 如果没有真实订单数据，添加一些静态示例订单（展示不同状态）
        if not order_list:
            sample_orders = [
                {
                    'order_id': 1,
                    'car_id': 1,
                    'pickup_store_id': 1,
                    'return_store_id': 1,
                    'start_time': '2024-01-15T10:00:00',
                    'end_time': '2024-01-18T10:00:00',
                    'total_amount': 900.00,
                    'actual_amount': 900.00,
                    'discount_amount': 0.00,
                    'create_time': '2024-01-14T15:30:00',
                    'update_time': '2024-01-14T15:30:00',
                    'status': 0,
                    'status_description': '待支付',
                    'name': '订单 001',
                    'image': '/assets/images/c1.png'
                },
                {
                    'order_id': 2,
                    'car_id': 2,
                    'pickup_store_id': 1,
                    'return_store_id': 2,
                    'start_time': '2024-01-20T09:00:00',
                    'end_time': '2024-01-22T18:00:00',
                    'total_amount': 600.00,
                    'actual_amount': 540.00,
                    'discount_amount': 60.00,
                    'create_time': '2024-01-19T14:20:00',
                    'update_time': '2024-01-19T16:45:00',
                    'status': 1,
                    'status_description': '已支付',
                    'name': '订单 002',
                    'image': '/assets/images/c2.png'
                },
                {
                    'order_id': 3,
                    'car_id': 3,
                    'pickup_store_id': 2,
                    'return_store_id': 1,
                    'start_time': '2024-01-10T08:00:00',
                    'end_time': '2024-01-12T20:00:00',
                    'total_amount': 750.00,
                    'actual_amount': 750.00,
                    'discount_amount': 0.00,
                    'create_time': '2024-01-09T11:15:00',
                    'update_time': '2024-01-12T20:30:00',
                    'status': 2,
                    'status_description': '已完成',
                    'name': '订单 003',
                    'image': '/assets/images/c3.png'
                }
            ]
            order_list.extend(sample_orders)
        
        return jsonify({
            "status": "success",
            "orders": order_list
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"获取订单失败: {str(e)}"
        }), 500

# 获取城市网点数据的API端点
@app.route('/api/redis/city-branches', methods=['GET'])
def get_city_branches():
    try:
        # 从Redis获取城市网点数据
        city_data = redis_client.hgetall('city_branches')
        
        # 如果Redis中没有数据，初始化默认数据
        if not city_data:
            default_data = {
                '上海': '10',
                '浙江': '15', 
                '北京': '8',
                '广州': '12',
                '深圳': '9'
            }
            redis_client.hmset('city_branches', default_data)
            city_data = default_data
        
        # 转换数据类型
        result = {city: int(count) for city, count in city_data.items()}
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 获取车辆租赁数据的API端点
@app.route('/api/redis/vehicle-rentals', methods=['GET'])
def get_vehicle_rentals():
    try:
        # 从Redis获取车辆租赁数据
        rental_data = redis_client.hgetall('vehicle_rentals')
        
        # 如果Redis中没有数据，初始化默认数据
        if not rental_data:
            default_data = {
                '本田雅阁': '20',
                '本田思域': '18',
                '丰田凯美瑞': '22',
                '大众帕萨特': '8',
                '现代索纳塔': '6'
            }
            redis_client.hmset('vehicle_rentals', default_data)
            rental_data = default_data
        
        # 转换数据类型
        result = {vehicle: int(count) for vehicle, count in rental_data.items()}
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            # 创建数据库表
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")
        
        try:
            # 初始化MinIO存储桶
            print("Initializing MinIO...")
            create_bucket_if_not_exists()
            print("MinIO bucket check completed.")
        except Exception as e:
            print(f"Error with MinIO bucket: {e}")
        
        try:
            # 迁移本地图片到MinIO（仅在首次运行时）
            local_images_path = os.path.join('car-rental', 'src', 'assets', 'images')
            if os.path.exists(local_images_path):
                print("Migrating local images to MinIO...")
                migration_map = migrate_local_images_to_minio(local_images_path)
                print(f"Migrated {len(migration_map)} images to MinIO")
        except Exception as e:
            print(f"Error migrating images: {e}")
        
        try:
            # 创建Elasticsearch索引
            create_index_if_not_exists()
            print("Elasticsearch index check completed.")
        except Exception as e:
            print(f"Error with Elasticsearch: {e}")
        
        try:
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
        except Exception as e:
            print(f"Error syncing data: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
