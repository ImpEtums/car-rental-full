const mysql = require('mysql2/promise');
const logger = require('./log'); // 确保 logger 路径正确

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
        logger.info('Database pool successfully created and tested a connection.');
        connection.release(); // 释放连接回连接池
    })
    .catch(err => {
        logger.error('Database connection failed: %s', err.message);
        logger.error('DB_HOST: %s, DB_USER: %s, DB_DATABASE: %s', process.env.DB_HOST, process.env.DB_USER, process.env.DB_DATABASE);
        // 考虑在这里退出进程，如果数据库连接是必需的
        process.exit(1); 
    });

module.exports = pool;