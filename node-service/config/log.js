const { createLogger, format, transports } = require('winston');
const { combine, timestamp, printf, colorize, align, splat } = format; // <-- 在这里添加了 splat

const logFormat = printf(({ level, message, timestamp }) => {
  return `${timestamp} ${level}: ${message}`;
});

const logger = createLogger({
  level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
  format: combine(
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    splat(), // <-- 在这里添加了 splat()
    logFormat
  ),
  transports: [
    new transports.Console({
      format: combine(
        colorize(),
        align(),
        logFormat
      )
    }),
    new transports.File({ filename: 'logs/error.log', level: 'error' }),
    new transports.File({ filename: 'logs/application.log' })
  ],
});

module.exports = logger;