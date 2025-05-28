# MinIO 安装和配置指南

本文档将指导您如何安装和配置MinIO对象存储服务，用于存储车辆图片。

## 1. MinIO 安装

### Windows 安装

1. 下载MinIO服务器：
   ```bash
   # 使用PowerShell下载
   Invoke-WebRequest -Uri "https://dl.min.io/server/minio/release/windows-amd64/minio.exe" -OutFile "minio.exe"
   ```

2. 创建数据目录：
   ```bash
   mkdir C:\minio-data
   ```

3. 启动MinIO服务器：
   ```bash
   .\minio.exe server C:\minio-data --console-address ":9001"
   ```

### Linux/macOS 安装

1. 下载并安装MinIO：
   ```bash
   # Linux
   wget https://dl.min.io/server/minio/release/linux-amd64/minio
   chmod +x minio
   
   # macOS
   brew install minio/stable/minio
   ```

2. 创建数据目录：
   ```bash
   mkdir ~/minio-data
   ```

3. 启动MinIO服务器：
   ```bash
   ./minio server ~/minio-data --console-address ":9001"
   ```

## 2. MinIO 配置

### 默认访问信息

启动MinIO后，您将看到以下信息：
- **API地址**: http://localhost:9000
- **控制台地址**: http://localhost:9001
- **默认用户名**: minioadmin
- **默认密码**: minioadmin

### 访问MinIO控制台

1. 打开浏览器访问 http://localhost:9001
2. 使用默认凭据登录（minioadmin/minioadmin）
3. 建议创建新的访问密钥和秘密密钥

### 创建存储桶

1. 在MinIO控制台中，点击"Create Bucket"
2. 输入存储桶名称：`car-images`
3. 点击"Create Bucket"创建

### 配置公共访问（可选）

如果您希望图片可以公开访问，需要设置存储桶策略：

1. 在存储桶页面，点击"Manage" -> "Access Rules"
2. 添加以下策略：
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::car-images/*"
       }
     ]
   }
   ```

## 3. 项目配置

### 修改配置文件

编辑 `minio_config.py` 文件，根据您的MinIO设置修改配置：

```python
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',      # 您的MinIO服务器地址
    'access_key': 'your_access_key',   # 您的访问密钥
    'secret_key': 'your_secret_key',   # 您的秘密密钥
    'secure': False,                   # 如果使用HTTPS则设为True
    'bucket_name': 'car-images',       # 存储桶名称
}
```

### 安装Python依赖

确保已安装MinIO Python客户端：

```bash
pip install minio
```

## 4. 使用说明

### 图片上传

项目启动后，您可以通过以下API上传车辆图片：

```bash
# 上传图片
curl -X POST -F "file=@car_image.jpg" http://localhost:5000/api/upload_car_image
```

### 图片访问

上传成功后，您将获得图片的访问URL，可以直接在浏览器中访问。

### 自动迁移

项目首次启动时，会自动将 `car-rental/src/assets/images` 目录中的图片迁移到MinIO。

## 5. 故障排除

### 常见问题

1. **连接失败**
   - 检查MinIO服务是否正在运行
   - 确认端口9000没有被其他服务占用
   - 检查防火墙设置

2. **权限错误**
   - 确认访问密钥和秘密密钥正确
   - 检查存储桶是否存在
   - 验证存储桶权限设置

3. **上传失败**
   - 检查文件大小是否超过限制
   - 确认文件类型是否被允许
   - 查看服务器日志获取详细错误信息

### 日志查看

MinIO服务器日志会显示详细的操作信息，有助于诊断问题。

## 6. 生产环境建议

1. **安全性**
   - 更改默认的访问密钥和秘密密钥
   - 启用HTTPS
   - 配置适当的存储桶策略

2. **性能**
   - 使用SSD存储
   - 配置适当的内存和CPU资源
   - 考虑使用分布式部署

3. **备份**
   - 定期备份数据
   - 配置数据复制
   - 监控存储使用情况

## 7. 更多资源

- [MinIO官方文档](https://docs.min.io/)
- [MinIO Python客户端文档](https://docs.min.io/docs/python-client-quickstart-guide.html)
- [MinIO最佳实践](https://docs.min.io/docs/minio-server-configuration-guide.html)