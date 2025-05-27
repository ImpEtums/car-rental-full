# elasticsearch_utils.py
from elasticsearch import Elasticsearch

# 连接 Elasticsearch
# 注意：请根据您的实际配置修改主机、端口和认证信息
es = Elasticsearch(
    ['https://localhost:9200'], # 保持 HTTPS
    http_auth=('elastic', 'qsV3G3zVF-41Nlnx5sIp'),
    verify_certs=False # 禁用 SSL 证书验证 (仅限开发环境)
)

def create_index_if_not_exists(index_name='cars'):
    """如果索引不存在，则创建它。"""
    if not es.indices.exists(index=index_name):
        # 定义索引的映射（可选，但推荐）
        mappings = {
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "brand": {"type": "keyword"}, # 品牌通常用于精确匹配或聚合
                    "model": {"type": "text"},
                    "seats": {"type": "integer"},
                    "fuel_type": {"type": "keyword"},
                    "transmission": {"type": "keyword"},
                    "price_per_day": {"type": "float"},
                    "image_url": {"type": "keyword", "index": False}, # 图片URL通常不需要搜索，不索引
                    "description": {"type": "text"} # 可以添加车辆描述等字段
                }
            }
        }
        es.indices.create(index=index_name, body=mappings)
        print(f"Index '{index_name}' created.")
    else:
        print(f"Index '{index_name}' already exists.")

def index_car_data(car_data, index_name='cars'):
    """将单条车辆数据索引到 Elasticsearch。"""
    try:
        es.index(index=index_name, id=car_data.get('id'), document=car_data)
        print(f"Car {car_data.get('name')} indexed successfully.")
    except Exception as e:
        print(f"Error indexing car {car_data.get('name')}: {e}")

def bulk_index_cars(index_name='cars', cars_data=None):
    """批量索引车辆数据。"""
    if cars_data is None:
        cars_data = []
    
    from elasticsearch.helpers import bulk
    actions = [
        {
            "_index": index_name,
            "_id": car.get('id'),
            "_source": car
        }
        for car in cars_data
    ]
    try:
        successes, errors = bulk(es, actions, raise_on_error=False)
        print(f"Successfully indexed {len(cars_data)} cars to index '{index_name}'.")
        if errors:
            print(f"Errors occurred during bulk indexing: {errors}")
    except Exception as e:
        print(f"Error during bulk indexing: {e}")

def search_cars(query_string, index_name='cars'):
    """根据查询字符串搜索车辆。"""
    # 基础的多字段匹配查询
    # 您可以根据需求构建更复杂的查询，例如使用布尔查询组合多个条件
    query_body = {
        "query": {
            "multi_match": {
                "query": query_string,
                "fields": ["name", "brand", "model", "description"], # 搜索这些字段
                "fuzziness": "AUTO" # 允许一定的拼写错误
            }
        }
    }
    print(f"Elasticsearch query body: {query_body}") # 打印查询体
    try:
        response = es.search(index=index_name, body=query_body)
        print(f"Elasticsearch response: {response}") # 打印原始响应
        hits = [hit['_source'] for hit in response['hits']['hits']]
        return hits
    except Exception as e:
        print(f"Error searching cars: {e}")
        return []

# --- 数据库同步相关函数 ---
# 以下函数用于将前端的车辆数据同步到数据库，并随后索引到Elasticsearch

def format_car_data_for_db(frontend_car):
    """将前端车辆数据格式化为符合数据库 car_info 表的结构。"""
    # 注意：这里需要根据 car_info 表的实际字段进行调整
    # 例如，type_id 可能需要从 car_type_info 表查询得到
    # rental_status, car_condition 等字段也需要根据业务逻辑设置初始值
    return {
        'car_id': frontend_car.get('id'),
        'type_id': None, # 假设需要后续填充或从其他表关联
        'car_number': f"CAR-{frontend_car.get('id')}", # 示例车牌号
        'brand': frontend_car.get('name', '').split(' ')[0] if frontend_car.get('name') else None, # 简单提取品牌
        'model': ' '.join(frontend_car.get('name', '').split(' ')[1:]) if frontend_car.get('name') else None, # 简单提取型号
        'color': None, # 假设颜色信息不在前端数据中
        'buy_time': None, # 购买时间
        'mileage': 0, # 初始里程
        'rental_status': 0, # 0: 可用, 1: 已租, 2: 维护中 (示例)
        'car_condition': 0, # 0: 良好, 1: 一般, 2: 需维修 (示例)
        'transmission_type': 0 if frontend_car.get('transmission') == '自动' else 1, # 0: 自动, 1: 手动 (示例)
        'fuel_type': 0 if frontend_car.get('fuelType') == '汽油' else (1 if frontend_car.get('fuelType') == '柴油' else 2), # 0: 汽油, 1: 柴油, 2: 电动 (示例)
        'engine_capacity': None,
        'gps_device': None,
        'last_maintain_time': None,
        'next_maintain_mileage': None,
        'car_images': frontend_car.get('image') # 存储图片路径或MinIO的key
    }

def generate_insert_sql(table_name, data_dict):
    """生成插入语句。"""
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['%s'] * len(data_dict))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE "
    update_clauses = [f"{col}=VALUES({col})" for col in data_dict.keys() if col != 'car_id'] # car_id是主键，不应在UPDATE中
    sql += ", ".join(update_clauses)
    return sql, list(data_dict.values())


if __name__ == '__main__':
    # 示例：创建索引
    create_index_if_not_exists()

    # 示例：从前端获取的车辆数据 (模拟)
    # 实际应用中，这些数据应该从 CarShowcasePage.vue 中提取或通过API获取
    sample_cars_from_frontend = [
        {
            "id": 1,
            "name": '本田雅阁',
            "image": '../assets/images/car1.png', # 注意：ES中最好存储可访问的URL或MinIO的key
            "seats": 5,
            "fuelType": '汽油',
            "transmission": '自动',
            "price": 358
        },
        {
            "id": 2,
            "name": '本田思域',
            "image": '../assets/images/car2.png',
            "seats": 5,
            "fuelType": '汽油',
            "transmission": '自动',
            "price": 328
        },
        # ... 可以添加更多车辆数据
    ]

    # 格式化并准备索引到ES的数据
    cars_for_es = []
    print("--- SQL INSERT Statements (for reference) ---")
    for car_fe in sample_cars_from_frontend:
        # 1. 格式化数据以存入数据库
        db_car_data = format_car_data_for_db(car_fe)
        # 2. 生成SQL语句 (实际应用中会执行这些SQL)
        sql, values = generate_insert_sql('car_info', db_car_data)
        print(f"{sql} -- VALUES: {values}")
        
        # 3. 准备用于ES的数据 (可以与数据库字段略有不同，更侧重搜索)
        es_car_data = {
            'id': car_fe.get('id'),
            'name': car_fe.get('name'),
            'brand': car_fe.get('name', '').split(' ')[0] if car_fe.get('name') else None,
            'model': ' '.join(car_fe.get('name', '').split(' ')[1:]) if car_fe.get('name') else None,
            'seats': car_fe.get('seats'),
            'fuel_type': car_fe.get('fuelType'),
            'transmission': car_fe.get('transmission'),
            'price_per_day': car_fe.get('price'),
            'image_url': car_fe.get('image'), # 考虑转换为绝对URL或MinIO key
            'description': f"{car_fe.get('name')} 是一款{car_fe.get('seats')}座{car_fe.get('fuelType')}{car_fe.get('transmission')}车，日租金{car_fe.get('price')}元。"
        }
        cars_for_es.append(es_car_data)
    print("---------------------------------------------")

    # 批量索引到Elasticsearch
    if cars_for_es:
        bulk_index_cars('cars', cars_for_es)

    # 示例：搜索车辆
    print("\n--- Searching for '本田' ---")
    search_results = search_cars("本田")
    for car in search_results:
        print(car)
    
    print("\n--- Searching for '雅阁 自动' ---")
    search_results_accord = search_cars("雅阁 自动")
    for car in search_results_accord:
        print(car)