# WebService 使用示例

本文档展示如何使用新添加的WebService功能，支持XML和SOAP格式的请求和响应。

## 功能特性

- 自动检测请求格式（JSON/XML/SOAP）
- 根据Accept头返回相应格式的响应
- 支持传统的SOAP WebService
- 保持与现有JSON API的完全兼容

## XML格式请求示例

### 1. 搜索车辆（XML请求）

**请求：**
```bash
curl -X GET "http://localhost:5000/api/search_cars?q=Toyota" \
  -H "Accept: application/xml"
```

**XML响应：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <item>
        <id>1</id>
        <name>Toyota Camry</name>
        <brand>Toyota</brand>
        <model>Camry</model>
        <price_per_day>300</price_per_day>
        <availability>true</availability>
    </item>
</response>
```

### 2. 用户注册（XML请求）

**请求：**
```bash
curl -X POST "http://localhost:5000/api/register_user" \
  -H "Content-Type: application/xml" \
  -H "Accept: application/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<user>
    <username>testuser</username>
    <email>test@example.com</email>
    <password>password123</password>
    <real_name>测试用户</real_name>
    <phone>13800138000</phone>
    <id_number>123456789012345678</id_number>
</user>'
```

**XML响应：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <success>true</success>
</response>
```

### 3. 用户登录（XML请求）

**请求：**
```bash
curl -X POST "http://localhost:5000/api/login" \
  -H "Content-Type: application/xml" \
  -H "Accept: application/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<login>
    <username>testuser</username>
    <password>password123</password>
</login>'
```

**XML响应：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <message>登录成功</message>
    <status>success</status>
    <user>
        <user_id>1</user_id>
        <username>testuser</username>
        <email>test@example.com</email>
    </user>
</response>
```

## SOAP格式请求示例

### 1. SOAP搜索车辆

**请求：**
```bash
curl -X GET "http://localhost:5000/api/search_cars?q=Honda" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H "SOAPAction: \"SearchCars\""
```

**SOAP响应：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <SearchCarsResponse>
            <item>
                <id>2</id>
                <name>Honda Civic</name>
                <brand>Honda</brand>
                <model>Civic</model>
                <price_per_day>280</price_per_day>
                <availability>true</availability>
            </item>
        </SearchCarsResponse>
    </soap:Body>
</soap:Envelope>
```

### 2. SOAP用户登录

**请求：**
```bash
curl -X POST "http://localhost:5000/api/login" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H "SOAPAction: \"Login\"" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <Login>
            <username>testuser</username>
            <password>password123</password>
        </Login>
    </soap:Body>
</soap:Envelope>'
```

**SOAP响应：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <LoginResponse>
            <message>登录成功</message>
            <status>success</status>
            <user>
                <user_id>1</user_id>
                <username>testuser</username>
                <email>test@example.com</email>
            </user>
        </LoginResponse>
    </soap:Body>
</soap:Envelope>
```

## 错误处理示例

### XML错误响应
```xml
<?xml version="1.0" encoding="UTF-8"?>
<error_response>
    <error>
        <message>用户名已存在</message>
        <code>400</code>
    </error>
</error_response>
```

### SOAP错误响应（Fault）
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <soap:Fault>
            <faultcode>Server</faultcode>
            <faultstring>服务器错误: 数据库连接失败</faultstring>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>
```

## 兼容性说明

1. **JSON API保持不变**：所有现有的JSON API调用方式完全不受影响
2. **自动格式检测**：根据Content-Type和Accept头自动选择响应格式
3. **向后兼容**：如果不指定XML相关的头信息，API行为与之前完全一致

## 支持的Content-Type

- `application/json` - JSON格式（默认）
- `application/xml` - XML格式
- `text/xml` - XML格式（SOAP兼容）
- `application/soap+xml` - SOAP格式

## 支持的Accept头

- `application/json` - 返回JSON响应（默认）
- `application/xml` - 返回XML响应
- `text/xml` - 返回XML响应（SOAP兼容）

## 测试建议

1. 使用Postman或类似工具测试不同格式的请求
2. 确保设置正确的Content-Type和Accept头
3. 验证XML格式的正确性
4. 测试错误场景的处理

## 注意事项

1. XML请求中的数据结构应与JSON请求保持一致
2. 复杂的嵌套数据在XML中会被适当转换
3. 文件上传等二进制数据操作建议继续使用原有的multipart/form-data格式
4. Session和Cookie机制在XML/SOAP请求中同样有效