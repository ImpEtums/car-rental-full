// node-api/config/logger.js
const winston = require('winston');
const path = require('path'); // 引入 path 模块用于处理文件路径
const fs = require('fs');   // 引入 fs 模块用于检查和创建目录

// 定义日志文件存储目录
const logDir = path.join(__dirname, '..', 'logs'); // 日志文件将存储在项目根目录下的 'logs' 文件夹中

// 确保日志目录存在，如果不存在则创建
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

const logger = winston.createLogger({
  level: 'debug', // 默认日志级别设置为 'debug'，意味着所有级别（debug, info, warn, error等）的日志都会被捕获

  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), // 添加时间戳
    winston.format.errors({ stack: true }), // 捕获错误堆栈信息
    winston.format.splat(), // 允许使用 printf 风格的字符串格式化，例如 logger.info('User %s logged in', username);
    winston.format.json() // 将日志输出为 JSON 格式，便于机器解析和日志管理系统集成
  ),

  transports: [
    // 1. 控制台输出：用于开发和即时监控
    new winston.transports.Console({
      level: 'debug', // 控制台也显示 debug 级别及以上的日志
      format: winston.format.combine(
        winston.format.colorize(), // 在控制台输出彩色日志，增强可读性
        winston.format.simple()    // 控制台输出简洁格式，易于人类阅读
      )
    }),

    // 2. 文件输出 - 记录所有级别日志：通常命名为 combined.log 或 app.log
    new winston.transports.File({
      filename: path.join(logDir, 'combined.log'), // 文件路径
      level: 'debug', // 写入这个文件的最低日志级别是 'info'。这意味着 debug 级别的日志不会被写入这里，但会显示在控制台。
      maxsize: 5 * 1024 * 1024, // 日志文件最大大小 5MB
      maxFiles: 5, // 最多保留 5 个日志文件（当文件达到 maxsize 时会自动滚动创建新文件）
      tailable: true // 在文件达到最大大小后，新的日志会追加到新文件中，旧文件会被保留（如果 maxFiles 允许）
    }),

    // 3. 文件输出 - 只记录错误日志：通常命名为 error.log
    new winston.transports.File({
      filename: path.join(logDir, 'error.log'), // 文件路径
      level: 'error', // 写入这个文件的最低日志级别是 'error'
      maxsize: 5 * 1024 * 1024,
      maxFiles: 5,
      tailable: true
    })
  ],

  // 捕获和记录未捕获的异常 (uncaught exceptions)
  exceptionHandlers: [
    new winston.transports.File({ filename: path.join(logDir, 'exceptions.log') })
  ],

  // 捕获和记录未处理的 Promise 拒绝 (unhandled promise rejections)
  rejectionHandlers: [
    new winston.transports.File({ filename: path.join(logDir, 'rejections.log') })
  ]
});

module.exports = logger;