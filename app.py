import json
from datetime import datetime

import bcrypt
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

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
with app.app_context():
    db.create_all()

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

@app.route('/api/register_user', methods=['POST'])
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


@app.route('/api/login', methods=['POST'])
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


@app.route('/api/get_user_info', methods=['GET'])
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

@app.route('/api/update_user_info', methods=['PUT'])
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

@app.route('/api/logout', methods=['POST'])
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
    app.run(debug=True)
