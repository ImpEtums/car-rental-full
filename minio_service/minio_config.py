# MinIO配置文件
# 请根据您的MinIO服务器配置修改以下参数

# MinIO服务器配置
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',      # MinIO服务器地址和端口
    'access_key': 'minioadmin',        # 访问密钥
    'secret_key': 'minioadmin',        # 秘密密钥
    'secure': False,                   # 是否使用HTTPS
    'bucket_name': 'car-images',       # 存储桶名称
    'region': 'us-east-1'              # 区域（可选）
}

# 文件上传配置
UPLOAD_CONFIG = {
    'max_file_size': 10 * 1024 * 1024,  # 最大文件大小（10MB）
    'allowed_extensions': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},  # 允许的文件扩展名
    'upload_folder': 'cars',            # MinIO中的上传文件夹
}

# URL配置
URL_CONFIG = {
    'presigned_url_expiry_hours': 1,    # 预签名URL过期时间（小时）
    'public_url_enabled': True,         # 是否启用公共URL访问
}

# 开发环境配置
DEV_CONFIG = {
    'auto_migrate_local_images': True,  # 是否自动迁移本地图片
    'local_images_path': 'car-rental/src/assets/images',  # 本地图片路径
    'debug_mode': True,                 # 调试模式
}