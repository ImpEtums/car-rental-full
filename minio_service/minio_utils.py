from minio import Minio
from minio.error import S3Error
import os
from datetime import timedelta
from werkzeug.utils import secure_filename
import uuid

# 导入配置
from .minio_config import MINIO_CONFIG, UPLOAD_CONFIG, URL_CONFIG

# MinIO 配置
MINIO_ENDPOINT = MINIO_CONFIG['endpoint']
MINIO_ACCESS_KEY = MINIO_CONFIG['access_key']
MINIO_SECRET_KEY = MINIO_CONFIG['secret_key']
MINIO_SECURE = MINIO_CONFIG['secure']
BUCKET_NAME = MINIO_CONFIG['bucket_name']

# 初始化MinIO客户端
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def set_bucket_public_read_policy(bucket_name=BUCKET_NAME):
    """设置bucket为公共只读访问策略"""
    try:
        # 设置bucket为公共只读权限（更安全的策略）
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        
        import json
        minio_client.set_bucket_policy(bucket_name, json.dumps(policy))
        print(f"Bucket '{bucket_name}' set to public read-only access.")
        return True
    except S3Error as e:
        print(f"Error setting bucket policy: {e}")
        return False

def create_bucket_if_not_exists(bucket_name=BUCKET_NAME):
    """如果存储桶不存在则创建它，并设置为公共只读访问"""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
            
            # 设置为公共只读访问
            set_bucket_public_read_policy(bucket_name)
        else:
            print(f"Bucket '{bucket_name}' already exists.")
            # 可选：为现有bucket也设置公共只读策略
            # set_bucket_public_read_policy(bucket_name)
    except S3Error as e:
        print(f"Error creating bucket: {e}")
        return False
    return True

def upload_file_to_minio(file_path, object_name=None, bucket_name=BUCKET_NAME):
    """上传文件到MinIO
    
    Args:
        file_path (str): 本地文件路径
        object_name (str): MinIO中的对象名称，如果为None则使用文件名
        bucket_name (str): 存储桶名称
    
    Returns:
        str: 成功时返回对象名称，失败时返回None
    """
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        # 确保存储桶存在
        create_bucket_if_not_exists(bucket_name)
        
        # 上传文件
        minio_client.fput_object(bucket_name, object_name, file_path)
        print(f"File '{file_path}' uploaded as '{object_name}' to bucket '{bucket_name}'.")
        return object_name
    except S3Error as e:
        print(f"Error uploading file: {e}")
        return None

def upload_file_data_to_minio(file_data, file_name, bucket_name=BUCKET_NAME):
    """上传文件数据到MinIO
    
    Args:
        file_data: 文件数据流
        file_name (str): 文件名
        bucket_name (str): 存储桶名称
    
    Returns:
        str: 成功时返回对象名称，失败时返回None
    """
    try:
        # 检查文件扩展名
        file_extension = os.path.splitext(file_name)[1].lower()
        if file_extension.lstrip('.') not in UPLOAD_CONFIG['allowed_extensions']:
            print(f"File type {file_extension} not allowed")
            return None
        
        # 生成唯一的对象名称
        upload_folder = UPLOAD_CONFIG['upload_folder']
        object_name = f"{upload_folder}/{uuid.uuid4()}{file_extension}"
        
        # 确保存储桶存在
        create_bucket_if_not_exists(bucket_name)
        
        # 上传文件数据
        minio_client.put_object(
            bucket_name, 
            object_name, 
            file_data, 
            length=-1, 
            part_size=10*1024*1024
        )
        print(f"File data uploaded as '{object_name}' to bucket '{bucket_name}'.")
        return object_name
    except S3Error as e:
        print(f"Error uploading file data: {e}")
        return None

def get_file_url(object_name, bucket_name=BUCKET_NAME, expires=None):
    """获取文件的预签名URL
    
    Args:
        object_name (str): MinIO中的对象名称
        bucket_name (str): 存储桶名称
        expires (timedelta): URL过期时间，如果为None则使用配置文件中的默认值
    
    Returns:
        str: 预签名URL，失败时返回None
    """
    try:
        if expires is None:
            expires = timedelta(hours=URL_CONFIG['presigned_url_expiry_hours'])
        url = minio_client.presigned_get_object(bucket_name, object_name, expires=expires)
        return url
    except S3Error as e:
        print(f"Error generating presigned URL: {e}")
        return None

def get_public_file_url(object_name, bucket_name=BUCKET_NAME):
    """获取文件的公共访问URL（需要MinIO配置为公共访问）
    
    Args:
        object_name (str): MinIO中的对象名称
        bucket_name (str): 存储桶名称
    
    Returns:
        str: 公共访问URL
    """
    protocol = 'https' if MINIO_SECURE else 'http'
    return f"{protocol}://{MINIO_ENDPOINT}/{bucket_name}/{object_name}"

def delete_file_from_minio(object_name, bucket_name=BUCKET_NAME):
    """从MinIO删除文件
    
    Args:
        object_name (str): MinIO中的对象名称
        bucket_name (str): 存储桶名称
    
    Returns:
        bool: 成功时返回True，失败时返回False
    """
    try:
        minio_client.remove_object(bucket_name, object_name)
        print(f"File '{object_name}' deleted from bucket '{bucket_name}'.")
        return True
    except S3Error as e:
        print(f"Error deleting file: {e}")
        return False

def list_files_in_bucket(bucket_name=BUCKET_NAME, prefix=None):
    """列出存储桶中的文件
    
    Args:
        bucket_name (str): 存储桶名称
        prefix (str): 文件名前缀过滤
    
    Returns:
        list: 文件对象列表
    """
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]
    except S3Error as e:
        print(f"Error listing files: {e}")
        return []

def migrate_local_images_to_minio(local_images_dir, bucket_name=BUCKET_NAME):
    """将本地图片迁移到MinIO
    
    Args:
        local_images_dir (str): 本地图片目录路径
        bucket_name (str): 存储桶名称
    
    Returns:
        dict: 文件名到MinIO对象名称的映射
    """
    migration_map = {}
    
    if not os.path.exists(local_images_dir):
        print(f"Local images directory '{local_images_dir}' does not exist.")
        return migration_map
    
    # 确保存储桶存在
    create_bucket_if_not_exists(bucket_name)
    
    # 遍历本地图片文件
    for filename in os.listdir(local_images_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            local_file_path = os.path.join(local_images_dir, filename)
            
            # 生成MinIO对象名称
            file_extension = os.path.splitext(filename)[1]
            object_name = f"cars/{filename}"
            
            # 上传文件
            if upload_file_to_minio(local_file_path, object_name, bucket_name):
                migration_map[filename] = object_name
                print(f"Migrated: {filename} -> {object_name}")
    
    return migration_map

if __name__ == '__main__':
    # 测试MinIO连接和基本操作
    print("Testing MinIO connection...")
    
    # 创建存储桶
    create_bucket_if_not_exists()
    
    # 列出文件
    files = list_files_in_bucket()
    print(f"Files in bucket: {files}")
    
    print("MinIO setup completed successfully!")