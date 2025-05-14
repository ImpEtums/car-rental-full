# HZNU 汽车租赁系统

这是一个基于 Vue.js 前端和 Python Flask 后端的汽车租赁平台项目。

## 项目结构

```
├── car-rental/              # Vue.js 前端项目
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── axios.js
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   └── vite.config.js 
├── app.py                   # Python Flask 后端应用
├── requirements.txt         # Python 后端依赖
├── car_rent.sql             # 数据库SQL文件
├── 文档汇总/                  # 项目相关文档
└── README.md                # 本 README 文件 (项目根目录)
```

## 技术栈

*   **前端:** Vue 3, Vite, Vue Router, Naive UI, VueAMap (高德地图)
*   **后端:** Python, Flask, Flask-SQLAlchemy, Flask-CORS, PyMySQL, bcrypt
*   **数据库:** MySQL

## 环境要求

*   Node.js (推荐最新 LTS 版本，用于运行前端项目)
*   Python (推荐 3.8+ 版本，用于运行后端项目)
*   MySQL 数据库服务

## 运行指南

### 1. 数据库配置

1.  确保你的 MySQL 服务正在运行。
2.  创建一个名为 `car_rental` 的数据库。
3.  导入项目根目录下的 `car_rent.sql` 文件到 `car_rental` 数据库中。这会创建必要的表和初始数据。
4.  根据你的 MySQL 配置，修改后端 `app.py` 文件中的数据库连接字符串：
    ```python
    # app.py
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://your_mysql_user:your_mysql_password@your_mysql_host/car_rental'
    ```
    将 `your_mysql_user`, `your_mysql_password`, 和 `your_mysql_host` 替换为你的实际 MySQL 用户名、密码和主机地址（如果不是默认的 `root:root@localhost`）。

### 2. 后端启动 (Python Flask)

1.  打开终端，进入项目根目录 `HZNU_car_rental-main`。
2.  创建并激活 Python 虚拟环境 (推荐)：
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```
3.  安装后端依赖：
    ```bash
    pip install -r requirements.txt
    ```
4.  启动 Flask 应用：
    ```bash
    python app.py
    ```
    后端服务默认会在 `http://127.0.0.1:5000` 启动。

### 3. 前端启动 (Vue.js)

1.  打开新的终端，进入前端项目目录 `HZNU_car_rental-main/car-rental`。
2.  安装前端依赖：
    ```bash
    npm install
    ```
3.  启动 Vite 开发服务器：
    ```bash
    npm run dev
    ```
    前端应用默认会在 `http://localhost:5173` (或其他可用端口) 启动，并在浏览器中自动打开。


## 注意事项

*   后端 `app.py` 中的 `app.config['SECRET_KEY'] = 'your_secret_key'` 应该替换为一个更安全的密钥。
*   确保后端 CORS 配置 `CORS(app, origins="http://localhost:5173", supports_credentials=True)` 中的 `origins` 与你前端运行的地址和端口一致。