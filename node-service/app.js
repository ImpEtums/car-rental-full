require('dotenv').config();

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const logger = require('./config/log');
const authRoutes = require('./api/auth'); // 确保这里的路径是正确的

const app = express();


// CORS 配置 - 确保前端能跨域访问 Node.js
app.use(cors({
    origin: 'http://localhost:5173', // 你的 Vue 前端运行的地址
    credentials: true, // 允许携带 authorization header
    methods: ['GET', 'POST', 'PUT', 'DELETE'], // 允许的 HTTP 方法
    allowedHeaders: ['Content-Type', 'Authorization'], // 允许的请求头
}));

// 安全头设置
app.use(helmet());

// 请求体解析
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API 速率限制 (可选，但推荐)
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again after 15 minutes'
});
app.use('/api/', apiLimiter); // 对所有 /api/ 路径的请求应用速率限制

// 挂载路由
// 前端请求 /api/auth/me 会匹配到这里，然后由 authRoutes 中的 /me 处理
app.use('/api/auth', authRoutes); // 将认证相关的路由挂载到 /api/auth 路径下

// --- 错误处理中间件 ---
app.use((err, req, res, next) => {
    logger.error('Unhandled error: %s', err.stack);
    res.status(500).json({
        message: 'An unexpected error occurred!',
        detailedError: err.message,
        stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
    });
});

const PORT = process.env.NODE_PORT || 3000; // 或者你 .env 文件中配置的端口
app.listen(PORT, () => {
    logger.info(`Node.js API server running on port ${PORT}`);
});