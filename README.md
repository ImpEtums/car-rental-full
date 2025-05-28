# HZNU 汽车租赁系统

这是一个基于 Vue.js 前端和 Python Flask 后端的汽车租赁平台项目。

## 功能特性

- 用户注册和登录
- 浏览和筛选车辆
- 车辆预订
- 集成 Elasticsearch 实现车辆搜索

## 环境搭建与运行指南

### 1. 克隆仓库
   ```bash
   git clone <repository-url> # 请将 <repository-url> 替换为实际的仓库地址
   cd car-rental-full
   ```

### 2. 后端配置 (Flask, MySQL & Elasticsearch)

-   确保已安装并运行 Python, MySQL, 和 Elasticsearch。
-   **数据库配置:**
    1.  创建一个名为 `car_rental` 的 MySQL 数据库。
    2.  导入项目根目录下的 `car_rent.sql` 文件到 `car_rental` 数据库中。这将创建必要的表结构。
    3.  根据您的 MySQL 配置，修改后端 <mcfile name="app.py" path="c:\Users\DefineNX\Desktop\car-rental-full\app.py"></mcfile> 文件中的数据库连接字符串：
        ```python
        # app.py
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://your_mysql_user:your_mysql_password@your_mysql_host/car_rental'
        ```
        将 `your_mysql_user`, `your_mysql_password`, 和 `your_mysql_host` 替换为您的实际 MySQL 用户名、密码和主机地址（如果不是默认的 `root:root@localhost`）。
-   **安装 Python 依赖:**
    进入项目根目录 `car-rental-full`，建议创建并激活 Python 虚拟环境：
    ```bash
    python -m venv venv
    # Windows 系统激活:
    .\venv\Scripts\activate
    # macOS/Linux 系统激活:
    # source venv/bin/activate
    
    pip install -r requirements.txt
    ```
-   **Elasticsearch 配置:**
    -   应用程序默认连接到 `http://localhost:9200` 的 Elasticsearch 服务。您可以在 <mcfile name="elasticsearch_utils.py" path="c:\Users\DefineNX\Desktop\car-rental-full\elasticsearch_utils.py"></mcfile> 文件中修改此配置。
    -   **修改 Elasticsearch 默认密码:** 如果您刚安装 Elasticsearch，默认的 `elastic` 用户可能有一个生成的密码或者初始没有设置密码。要设置或更改 `elastic` 用户的密码：
        -   导航到您的 Elasticsearch 安装目录。
        -   运行密码重置工具。例如，在 Linux/macOS 上：
            ```bash
            ./bin/elasticsearch-reset-password -u elastic
            ```
            在 Windows 上：
            ```bash
            .\bin\elasticsearch-reset-password.bat -u elastic
            ```
        -   此命令将生成一个新密码，请记下它。
        -   如果您启用了认证，请更新 <mcfile name="elasticsearch_utils.py" path="c:\Users\DefineNX\Desktop\car-rental-full\elasticsearch_utils.py"></mcfile> 中的 `http_auth`：
            ```python
            es = Elasticsearch(
                ['http://localhost:9200'],
                http_auth=('elastic', '您的新ELASTIC_PASSWORD') 
            )
            ```
    -   **数据初始化:** 首次运行 Flask 后端时，系统会尝试：
        1.  创建必要的数据库表（如果它们不存在）。
        2.  通过车辆管理页面或直接向数据库添加车辆数据来填充 `car_info` 表。
        3.  创建一个名为 `cars` 的 Elasticsearch 索引（如果它不存在）。
        4.  将示例车辆数据索引到 Elasticsearch。
        这是一次性设置。如果 `car_info` 表中已有数据，则将跳过此初始同步。

-   **启动 Flask 开发服务器:**
    ```bash
    python app.py
    ```
    后端服务将在 `http://localhost:5000` 上可用。

### 3. 前端配置 (Vue.js)

-   导航到前端目录：
    ```bash
    cd car-rental
    ```
-   **安装 Node.js 依赖:**
    ```bash
    npm install
    ```
-   **启动 Vue 开发服务器:**
    ```bash
    npm run dev
    ```
    前端应用将在 `http://localhost:5173` (或其他可用端口) 上可用，并可能在浏览器中自动打开。

## 使用说明

-   打开浏览器并访问 `http://localhost:5173`。
-   注册新用户或使用已有账户登录。
-   浏览可用车辆。在车辆展示页面使用搜索框通过 Elasticsearch 查找车辆。

## 项目结构

```
├── car-rental/              # Vue.js 前端项目
│   ├── public/
│   ├── src/
│   │   ├── assets/          # 静态资源 (图片、图标等)
│   │   ├── components/      # Vue 组件
│   │   ├── router/          # Vue Router 路由配置
│   │   ├── services/        # API 服务调用
│   │   ├── App.vue          # 根组件
│   │   ├── main.js          # Vue 应用入口文件
│   │   └── axios.js         # Axios 配置文件 (如果使用)
│   ├── .gitignore
│   ├── index.html           # HTML 入口文件
│   ├── package.json         # npm 包管理文件
│   └── vite.config.js       # Vite 配置文件
├── app.py                   # Python Flask 后端主应用文件
├── elasticsearch_utils.py   # Elasticsearch 相关工具函数
├── requirements.txt         # Python 后端依赖列表
├── car_rent.sql             # MySQL 数据库结构和初始数据脚本
├── 文档汇总/                  # 项目相关设计文档、图表等
└── README.md                # 本 README 文件 (项目根目录)
```

## 技术栈

*   **前端:** Vue 3, Vite, Vue Router, Naive UI (或其他UI库), Axios (用于API请求)
*   **后端:** Python, Flask, Flask-SQLAlchemy (ORM), Flask-CORS, PyMySQL, bcrypt (密码哈希), Elasticsearch (搜索)
*   **数据库:** MySQL

## 注意事项

*   后端 `app.py` 中的 `app.config['SECRET_KEY'] = 'your_secret_key'` 应该替换为一个更安全的密钥。
*   确保后端 CORS 配置 `CORS(app, origins="http://localhost:5173", supports_credentials=True)` 中的 `origins` 与你前端运行的地址和端口一致。



# YJH聊天窗需要注意的地方
## 重要文件
/src/components/ChatInterface.vue
/src/components/Loginform.vue
/src/components/MessageItem.vue
/src/services/ChatService.js
在整个car-rental的文件夹当中：server.js
src/main.js和src/App.vue改过的我打好注释了

## 安装依赖
### 前端依赖
npm install element-plus vue ws

### '后端'依赖(此后端非彼后端)
npm install express ws memcached

### 启动memcached(win可能不一样)
memcached -d

## 启动后端服务器
node server.js

## 启动前端
npm run serve

上面两个启动一个之后访问就行，app.vue还没改，我怕给整个玩坏了

## MinIO 对象存储配置

本项目集成了 MinIO 对象存储服务用于管理车辆图片。以下是安装和配置步骤：

### 1. MinIO 服务器安装

#### Windows 系统
```powershell
# 使用 PowerShell 下载 MinIO
Invoke-WebRequest -Uri "https://dl.min.io/server/minio/release/windows-amd64/minio.exe" -OutFile "minio.exe"

# 创建数据目录
mkdir C:\minio-data

# 启动 MinIO 服务器
.\minio.exe server C:\minio-data --console-address ":9001"
```

#### Unix/Linux 系统
```bash
# 使用 wget 下载 MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio

# 创建数据目录
mkdir ~/minio-data

# 启动 MinIO 服务器
./minio server ~/minio-data --console-address ":9001"
```

#### macOS 系统
```bash
# 使用 Homebrew 安装（推荐）
brew install minio/stable/minio

# 或使用 wget 下载
wget https://dl.min.io/server/minio/release/darwin-amd64/minio
chmod +x minio

# 创建数据目录并启动
mkdir ~/minio-data
./minio server ~/minio-data --console-address ":9001"
```

### 2. MinIO 控制台访问

启动 MinIO 后，您可以通过以下方式访问：

- **API 地址**: http://localhost:9000
- **控制台地址**: http://localhost:9001
- **默认用户名**: minioadmin
- **默认密码**: minioadmin

### 3. 创建存储桶

1. 访问 MinIO 控制台：http://localhost:9001
2. 使用默认凭据登录（minioadmin/minioadmin）
3. 创建名为 `car-images` 的存储桶

### 4. 图片自动同步

项目启动时会自动将现有的车辆图片迁移到 MinIO：

```bash
# 启动 Flask 后端（会自动触发图片迁移）
python app.py
```

### 5. MinIO 配置说明

项目的 MinIO 配置位于 `minio_config.py` 文件中，您可以根据需要修改：

- 服务器地址和端口
- 访问密钥和秘密密钥
- 存储桶名称
- 文件上传限制

更多详细信息请参考项目根目录下的 `MINIO_SETUP.md` 文档。


### 新增功能与技术点

## 后端 (node-api)：

【新增项目】 独立的 node-api 后端服务项目：
提供用户注册、登录、个人信息获取等基于 JWT 的认证 API。
【新增集成】 集成 Winston 日志库，实现控制台和文件日志（logs/combined.log, logs/error.log）记录。

【主要改动文件】
- node-api/app.js 或 server.js：后端入口文件，可能包含数据库连接和中间件配置。
- node-api/config/logger.js：【新增文件】 或 【主要修改文件】，Winston 日志配置。
- node-api/routes/auth.js：【新增文件】 或 【主要修改文件】，处理用户认证相关的 API 路由。
- node-api/routes/user.js：【新增文件】 或 【主要修改文件】，处理用户个人资料相关的 API 路由（如 /api/auth/me）。
- node-api/models/user.js：【新增文件】 或 【主要修改文件】，用户数据模型定义。
- node-api/utils/ 目录下新增了 JWT 或其他辅助工具文件。

## 前端 (car-rental)：
【新增功能】 完整的用户登录、注册、个人信息展示页面。
【新增功能】 通过 Vue Router 导航守卫 实现路由鉴权，保护 /profile 等页面。
【主要改动文件】
- car-rental/src/components/Login.vue：【主要修改文件】，处理用户登录逻辑。
- car-rental/src/components/Register.vue：【主要修改文件】，处理用户注册逻辑。
- car-rental/src/components/Profile.vue：【新增文件】，用于展示用户个人信息。
- car-rental/src/router/index.js：【主要修改文件】，新增路由和导航守卫配置。
- car-rental/src/axios.js：【主要修改文件】，配置 Axios 实例，用于与后端 API 通信。
