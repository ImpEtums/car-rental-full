import log4js from 'log4js';

export const errorHandler = (err, req, res, next) => {
  const logger = log4js.getLogger('Error');
  logger.error(`路径 ${req.path} 发生错误: ${err.message}`);
  res.status(500).json({ message: '服务器内部错误' });
};