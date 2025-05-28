// node-api/app.js
require('dotenv').config(); // 确保在应用启动时加载 .env 文件中的环境变量

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');           // 引入安全头中间件
const rateLimit = require('express-rate-limit'); // 引入速率限制中间件

const logger = require('./config/logger'); // 确保这里的路径正确

const authRoutes = require('./routes/auth'); // 认证相关的路由

const app = express();

// --- 安全与性能增强中间件 ---

// CORS 配置 - 确保前端能跨域访问 Node.js
app.use(cors({
    origin: 'http://localhost:5173', // 您的 Vue 前端运行的地址
    credentials: true, // 允许携带 authorization header
    methods: ['GET', 'POST', 'PUT', 'DELETE'], // 允许的 HTTP 方法
    allowedHeaders: ['Content-Type', 'Authorization'], // 允许的请求头
}));

// 安全头设置：Helmet 帮助保护您的应用免受一些众所周知的 Web 漏洞的影响
app.use(helmet());

// 请求体解析：解析 JSON 和 URL-encoded 请求体
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// *** 新增：打印所有请求的 URL - 放在所有路由处理之前 ***
app.use((req, res, next) => {
    console.log(`Incoming Request: ${req.method} ${req.url}`);
    logger.debug(`Incoming Request: ${req.method} ${req.url}`);
    next();
});
// ********************************************************

// API 速率限制 (可选，但推荐)：防止暴力破解和拒绝服务攻击
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 分钟的时间窗口
    max: 100, // 在每个时间窗口内，每个 IP 最多允许 100 个请求
    message: '来自此 IP 的请求过多，请在 15 分钟后重试' // 超出限制时的返回信息
});
app.use('/api/', apiLimiter); // 对所有 /api/ 路径的请求应用速率限制

// --- 路由挂载 ---
// 将认证相关的路由挂载到 /api/auth 路径下
app.use('/api/auth', authRoutes);

// 简单的根路由，用于健康检查
app.get('/', (req, res) => {
    res.send('HZNU Node.js API 正在运行！');
});

// --- 错误处理中间件 ---
// 必须放在所有路由之后，用于捕获未被路由处理的错误
app.use((err, req, res, next) => {
    logger.error('未捕获的服务器错误：%s', err.stack); // 详细记录错误堆栈
    res.status(500).json({
        message: '服务器内部错误', // 对用户友好的通用错误信息
        detailedError: err.message, // 详细错误信息 (开发环境)
        stack: process.env.NODE_ENV === 'development' ? err.stack : undefined // 生产环境不暴露堆栈
    });
});

// --- 服务器启动 ---
const PORT = process.env.NODE_PORT || 3000; // 从 .env 文件获取端口，如果未定义则默认为 3000
app.listen(PORT, () => {
    logger.info(`Node.js API 服务器正在端口 ${PORT} 上运行`); // 使用日志记录
    console.log(`Node.js API 服务器正在端口 ${PORT} 上运行`); // 控制台输出，方便查看
});