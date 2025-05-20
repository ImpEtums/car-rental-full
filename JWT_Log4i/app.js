import express from 'express';
import log4js from 'log4js';
import { login } from './controllers/authController.js';
import { getCars, createOrder, getOrders } from './controllers/orderController.js';
import { authenticateJWT } from './middlewares/authMiddleware.js';
import { errorHandler } from './utils/logger.js';

const app = express();
app.use(express.json());

// 配置日志
log4js.configure({
  appenders: {
    file: { type: 'file', filename: 'logs/api.log' },
    console: { type: 'console' }
  },
  categories: {
    default: { appenders: ['file', 'console'], level: 'info' }
  }
});

// 公共接口：用户登录
app.post('/api/login', login);

// 需要认证的接口
app.get('/api/cars', authenticateJWT, getCars);       // 获取可租车辆
app.post('/api/orders', authenticateJWT, createOrder); // 创建订单
app.get('/api/orders', authenticateJWT, getOrders);   // 获取用户订单

// 错误处理
app.use(errorHandler);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`服务已启动: http://localhost:${PORT}`);
});