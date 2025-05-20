import jwt from 'jsonwebtoken';
import log4js from 'log4js';

const logger = log4js.getLogger('Auth');

// 模拟用户数据库
const mockUser = {
  id: 1,
  email: 'user@example.com',
  password: '123456', // 实际应存储哈希值
  role: 'customer'
};

export const login = (req, res) => {
  const { email, password } = req.body;
  
  if (email !== mockUser.email || password !== mockUser.password) {
    logger.error(`登录失败: ${email} 密码错误`);
    return res.status(401).json({ message: '邮箱或密码错误' });
  }

  // 生成 JWT Token（有效期1小时）
  const token = jwt.sign(
    { userId: mockUser.id, role: mockUser.role },
    process.env.JWT_SECRET,
    { expiresIn: '1h' }
  );

  logger.info(`用户 ${mockUser.id} 登录成功`);
  res.json({ token });
};