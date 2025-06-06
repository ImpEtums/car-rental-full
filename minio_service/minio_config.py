import os

# MinIO服务器配置 - 从环境变量获取
MINIO_CONFIG = {
    'endpoint': os.environ.get('MINIO_ENDPOINT', 'localhost:9000'),
    'access_key': os.environ.get('MINIO_ACCESS_KEY', 'minioadmin'),
    'secret_key': os.environ.get('MINIO_SECRET_KEY', 'minioadmin'),
    'secure': False,
    'bucket_name': 'car-images',
    'region': 'us-east-1'
}

# 文件上传配置
UPLOAD_CONFIG = {
    'max_file_size': 10 * 1024 * 1024,
    'allowed_extensions': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'upload_folder': 'cars',
}

# URL配置
URL_CONFIG = {
    'presigned_url_expiry_hours': 1,
    'public_url_enabled': True,
}

# 开发环境配置
DEV_CONFIG = {
    'auto_migrate_local_images': True,
    'local_images_path': 'car-rental/src/assets/images',
    'debug_mode': True,
}