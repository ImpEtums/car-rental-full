// node-api/config/db.js
const mysql = require('mysql2/promise');
const logger = require('./logger'); // 确保这里的路径正确，因为 logger.js 和 db.js 在同一个 config 文件夹下

// 确保这里从 process.env 获取环境变量
const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// 测试连接，仅用于启动时确认
pool.getConnection()
    .then(connection => {
        logger.info('数据库连接池创建成功，并测试了一个连接。');
        connection.release(); // 释放连接回连接池
    })
    .catch(err => {
        logger.error('数据库连接失败：%s', err.message);
        logger.error('DB_HOST: %s, DB_USER: %s, DB_DATABASE: %s', process.env.DB_HOST, process.env.DB_USER, process.env.DB_DATABASE);
        // 如果数据库连接是必需的，在这里退出进程
        process.exit(1);
    });

module.exports = pool;