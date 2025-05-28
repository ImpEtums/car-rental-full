#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新MinIO bucket策略为公共只读访问
"""

from minio_service.minio_utils import set_bucket_public_read_policy, minio_client
from minio_service.minio_config import MINIO_CONFIG
import json

def check_current_bucket_policy():
    """检查当前bucket策略"""
    bucket_name = MINIO_CONFIG['bucket_name']
    
    print(f"=== 检查bucket策略: {bucket_name} ===")
    
    try:
        if not minio_client.bucket_exists(bucket_name):
            print(f"❌ Bucket '{bucket_name}' 不存在")
            return False
            
        # 获取当前策略
        try:
            policy = minio_client.get_bucket_policy(bucket_name)
            if policy:
                policy_dict = json.loads(policy)
                print("\n📋 当前bucket策略:")
                print(json.dumps(policy_dict, indent=2, ensure_ascii=False))
                
                # 分析策略
                return analyze_policy(policy_dict)
            else:
                print("\n⚠️  Bucket没有设置策略（私有访问）")
                return False
        except Exception as e:
            print(f"\n⚠️  无法获取bucket策略: {e}")
            return False
            
    except Exception as e:
        print(f"检查bucket时出错: {e}")
        return False

def analyze_policy(policy_dict):
    """分析bucket策略"""
    statements = policy_dict.get('Statement', [])
    
    has_public_read = False
    has_write_permissions = False
    has_delete_permissions = False
    
    for statement in statements:
        if statement.get('Effect') == 'Allow' and statement.get('Principal', {}).get('AWS') == '*':
            actions = statement.get('Action', [])
            
            if 's3:GetObject' in actions:
                has_public_read = True
            
            if any(action in actions for action in ['s3:PutObject', 's3:AbortMultipartUpload']):
                has_write_permissions = True
                
            if 's3:DeleteObject' in actions:
                has_delete_permissions = True
    
    print("\n📊 策略分析:")
    print(f"✅ 公共读取权限: {'是' if has_public_read else '否'}")
    print(f"⚠️  公共写入权限: {'是' if has_write_permissions else '否'}")
    print(f"⚠️  公共删除权限: {'是' if has_delete_permissions else '否'}")
    
    if has_public_read and not has_write_permissions and not has_delete_permissions:
        print("\n✅ 策略配置正确：公共只读访问")
        return True
    elif has_public_read and (has_write_permissions or has_delete_permissions):
        print("\n⚠️  策略过于宽松：建议更新为只读访问")
        return False
    else:
        print("\n❌ 策略配置不正确：缺少公共读取权限")
        return False

def update_to_public_readonly():
    """更新bucket为公共只读访问"""
    bucket_name = MINIO_CONFIG['bucket_name']
    
    print(f"\n=== 更新bucket策略为公共只读: {bucket_name} ===")
    
    # 执行更新
    success = set_bucket_public_read_policy(bucket_name)
    
    if success:
        print("\n✅ Bucket策略已成功更新为公共只读访问")
        print("\n验证更新结果...")
        check_current_bucket_policy()
    else:
        print("\n❌ 更新bucket策略失败")
    
    return success

def test_public_url_access():
    """测试公共URL访问"""
    from minio_service.minio_utils import get_public_file_url, list_files_in_bucket
    
    bucket_name = MINIO_CONFIG['bucket_name']
    
    print(f"\n=== 测试公共URL访问 ===")
    
    # 列出bucket中的文件
    files = list_files_in_bucket(bucket_name)
    
    if not files:
        print("Bucket中没有文件可供测试")
        return
    
    # 取第一个文件进行测试
    test_file = files[0]
    public_url = get_public_file_url(test_file)
    
    print(f"测试文件: {test_file}")
    print(f"公共URL: {public_url}")
    print("\n💡 提示:")
    print("1. 复制上面的URL到浏览器中测试访问")
    print("2. 如果能正常访问图片，说明公共访问配置成功")
    print("3. 如果无法访问，可能需要检查MinIO服务器配置")

if __name__ == '__main__':
    print("MinIO Bucket策略管理工具")
    print("=" * 50)
    
    # 1. 检查当前策略
    policy_ok = check_current_bucket_policy()
    
    # 2. 如果策略不正确，提供更新选项
    if not policy_ok:
        print("\n建议更新bucket策略为安全的公共只读访问")
        update_to_public_readonly()
    
    # 3. 测试公共URL访问
    test_public_url_access()
    
    print("\n=== 使用说明 ===")
    print("1. 公共只读策略只允许读取文件，不允许写入或删除")
    print("2. 图片URL格式: http://localhost:9000/bucket-name/object-name")
    print("3. 应用程序会自动使用公共URL显示图片")
    print("4. 如果需要重新创建bucket，删除现有bucket后重启应用即可")