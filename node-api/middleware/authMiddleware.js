// node-api/middleware/authMiddleware.js
const { verifyToken } = require('../utils/jwt'); // 引入 JWT 验证函数
const logger = require('../config/logger');     // 引入日志器

/**
 * 认证中间件：验证请求头中的 JWT
 */
const authMiddleware = (req, res, next) => {
    // 从请求头中获取 Authorization 字段
    // 预期的格式是 "Bearer YOUR_JWT_TOKEN"
    const authHeader = req.headers['authorization'];

    // 1. 检查是否存在 Authorization 头
    if (!authHeader) {
        logger.warn('未提供 Authorization 头。');
        return res.status(401).json({ message: '未提供认证令牌' });
    }

    // 2. 解析 Token：从 "Bearer TOKEN" 中提取 TOKEN
    const token = authHeader.split(' ')[1];

    if (!token) {
        logger.warn('Authorization 头格式无效或未找到 Token。');
        return res.status(401).json({ message: '无效的认证令牌格式' });
    }

    // 3. 验证 Token
    const decoded = verifyToken(token);

    if (!decoded) {
        // verifyToken 会在内部记录详细的错误信息（如过期或无效）
        logger.error('令牌无效或已过期。');
        return res.status(403).json({ message: '令牌无效或已过期，请重新登录' });
    }

    // 4. Token 有效：将解码后的用户信息添加到请求对象中
    // 这样后续的路由处理函数就可以通过 req.user 访问用户信息
    req.user = decoded;
    logger.info(`用户 ${req.user.username || req.user.userId} 认证成功。`); // 记录认证成功的用户信息
    next(); // 继续处理下一个中间件或路由
};

module.exports = authMiddleware;