import jwt from 'jsonwebtoken';
import log4js from 'log4js';

const logger = log4js.getLogger('Auth');

export const authenticateJWT = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    logger.warn('未授权的请求，缺少 Token');
    return res.status(401).json({ message: '未授权' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      logger.error('Token 验证失败:', err.message);
      return res.status(403).json({ message: '无效 Token' });
    }
    req.user = decoded; // 将用户信息附加到请求对象
    next();
  });
};