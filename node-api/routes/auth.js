// node-api/routes/auth.js

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const dbPool = require('../config/db'); // 确保路径正确，db.js 在 config 文件夹中
const logger = require('../config/logger'); // 【重要修改】确保路径正确，logger.js 在 config 文件夹中

const router = express.Router();

// 确保 JWT_SECRET 在主入口文件（如 app.js）加载 .env 后可用
// 通常在 app.js 中引入 dotenv，这里直接使用 process.env
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRES_IN = '1h'; // JWT 有效期

// --- JWT 鉴权中间件 ---
// 这个中间件现在被定义在当前文件，并将在需要保护的路由中使用。
const authenticateToken = (req, res, next) => {
    logger.debug('尝试为 %s %s 认证令牌', req.method, req.url);
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // 期望格式 "Bearer TOKEN"

    if (token == null) {
        logger.warn('未为 %s %s 提供令牌', req.method, req.url);
        return res.status(401).json({ message: '未经授权：未提供令牌' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            logger.error('令牌验证失败为 %s %s：%s', req.method, req.url, err.message);
            if (err.name === 'TokenExpiredError') {
                return res.status(401).json({ message: '禁止访问：令牌已过期', error: err.message });
            }
            return res.status(403).json({ message: '禁止访问：无效令牌', error: err.message });
        }
        // 将解码后的用户信息（userId, username）存储在请求对象中，供后续路由使用
        req.user = user;
        logger.info('令牌已认证用户 ID: %d (用户名: %s)', user.userId, user.username);
        next(); // 继续处理下一个中间件或路由
    });
};

// --- 用户注册 API (POST /api/auth/register) ---
router.post('/register', async (req, res) => {
    const { username, email, password, real_name, phone, id_number } = req.body;
    logger.info('用户注册尝试，用户名: %s', username);

    if (!username || !email || !password || !real_name || !phone || !id_number) {
        logger.warn('注册尝试：缺少必填字段。');
        return res.status(400).json({ message: '所有注册字段都是必需的' });
    }

    let connection;
    try {
        connection = await dbPool.getConnection();

        // 检查用户名、邮箱、手机号或身份证号是否已被注册
        const [existingUsers] = await connection.execute(
            'SELECT user_id FROM user_info WHERE username = ? OR email = ? OR phone = ? OR id_number = ?',
            [username, email, phone, id_number]
        );

        if (existingUsers.length > 0) {
            logger.warn('注册尝试：已存在用户数据。');
            return res.status(409).json({ message: '用户名、邮箱、手机号或身份证号已被注册' });
        }

        const saltRounds = 10;
        const hashedPassword = await bcrypt.hash(password, saltRounds);
        logger.debug('为用户 %s 生成了哈希密码。', username);

        // 插入新用户到 user_info 表
        const [result] = await connection.execute(
            'INSERT INTO user_info (username, email, password, real_name, phone, id_number, register_time) VALUES (?, ?, ?, ?, ?, ?, NOW())', // 添加 register_time 字段并设置为当前时间
            [username, email, hashedPassword, real_name, phone, id_number]
        );

        logger.info('用户 %s (ID: %d) 注册成功。', username, result.insertId);
        res.status(201).json({ message: '用户注册成功', userId: result.insertId });

    } catch (error) {
        logger.error('用户 %s 注册过程中发生错误：%s', username, error.stack);
        res.status(500).json({
            message: '服务器内部错误',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

// --- 用户登录 API (POST /api/auth/login) ---
router.post('/login', async (req, res) => {
    const { username, password } = req.body;
    logger.info('用户登录尝试，用户名: %s', username);

    if (!username || !password) {
        logger.warn('登录尝试：缺少用户名或密码。');
        return res.status(400).json({ message: '用户名和密码都是必需的' });
    }

    let connection;
    try {
        connection = await dbPool.getConnection();

        const [rows] = await connection.execute(
            'SELECT user_id, username, password FROM user_info WHERE username = ?',
            [username]
        );

        const user = rows.length > 0 ? rows[0] : null;

        if (!user) {
            logger.warn('登录尝试：用户 %s 未找到。', username);
            return res.status(401).json({ message: '用户名或密码不正确' }); // 统一错误信息
        }

        const isMatch = await bcrypt.compare(password, user.password);

        if (!isMatch) {
            logger.warn('登录尝试：用户 %s 密码不匹配。', username);
            return res.status(401).json({ message: '用户名或密码不正确' }); // 统一错误信息
        }

        // 登录成功，生成 JWT
        const token = jwt.sign(
            { userId: user.user_id, username: user.username },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
        );

        logger.info('用户 %s (ID: %d) 登录成功。令牌已颁发。', user.username, user.user_id);
        res.json({
            message: '登录成功',
            token: token,
            userId: user.user_id,
            username: user.username
        });

    } catch (error) {
        logger.error('用户 %s 登录过程中发生错误：%s', username, error.stack);
        res.status(500).json({
            message: '服务器内部错误',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

// --- 获取当前登录用户的信息 API (GET /api/auth/me) ---
// 使用 authenticateToken 中间件来保护此路由
router.get('/me', authenticateToken, async (req, res) => {
    // authenticateToken 中间件会将解码后的用户信息（userId, username）放入 req.user
    logger.info('GET /auth/me - 正在为用户 ID: %d, 用户名: %s 获取个人资料', req.user.userId, req.user.username);

    let connection;
    try {
        connection = await dbPool.getConnection();
        // 从数据库获取更详细的用户信息，不包括密码
        // 确保 SELECT 的列与你的 user_info 表完全匹配，且是你需要返回的
        const [rows] = await connection.execute(
            'SELECT user_id, username, email, real_name, id_type, id_number, phone, register_time, driver_license, license_expire_date, emergency_contact, emergency_phone, credit_score FROM user_info WHERE user_id = ?',
            [req.user.userId] // 使用 Token 中解码出的 userId
        );

        if (rows.length === 0) {
            logger.warn('GET /auth/me - 未找到用户 ID: %d 的个人资料', req.user.userId);
            return res.status(404).json({ message: '未找到用户个人资料' });
        }

        const userProfile = rows[0];
        res.json({
            message: '用户个人资料获取成功',
            user: {
                userId: userProfile.user_id,
                username: userProfile.username,
                email: userProfile.email,
                realName: userProfile.real_name, // 注意这里是 camelCase
                phone: userProfile.phone,
                idNumber: userProfile.id_number, // 注意这里是 camelCase
                registerTime: userProfile.register_time, // 使用 register_time，并建议在前端处理日期格式
                driverLicense: userProfile.driver_license,
                licenseExpireDate: userProfile.license_expire_date,
                emergencyContact: userProfile.emergency_contact,
                emergencyPhone: userProfile.emergency_phone,
                creditScore: userProfile.credit_score
            }
        });

    } catch (error) {
        logger.error('GET /auth/me - 获取用户 ID %d 个人资料时发生错误：%s', req.user.userId, error.stack);
        res.status(500).json({
            message: '服务器内部错误',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

// --- 更新用户个人信息 API (PUT /api/auth/update_profile) ---
// 使用 authenticateToken 中间件来保护此路由
router.put('/update_profile', authenticateToken, async (req, res) => {
    logger.info('PUT /auth/update_profile - 正在为用户 ID: %d, 用户名: %s 尝试更新个人资料', req.user.userId, req.user.username);
    // 从请求体获取要更新的字段
    // 假设可以更新用户名、邮箱、手机号等
    const { username, email, phone, real_name, id_type, id_number, driver_license, license_expire_date, emergency_contact, emergency_phone, credit_score } = req.body;

    // 可以在这里添加更细致的输入验证 (例如，确保邮箱格式正确，手机号是数字等)
    if (!username && !email && !phone && !real_name && !id_type && !id_number && !driver_license && !license_expire_date && !emergency_contact && !emergency_phone && !credit_score) {
        logger.warn('PUT /auth/update_profile - 用户 ID: %d 未提供任何更新字段。', req.user.userId);
        return res.status(400).json({ message: '请提供至少一个要更新的字段。' });
    }

    let connection;
    try {
        connection = await dbPool.getConnection();

        // 动态构建 UPDATE 查询
        const fieldsToUpdate = [];
        const values = [];

        if (username !== undefined) {
            // 检查更新后的用户名是否已存在 (除了当前用户自己)
            const [existingUsers] = await connection.execute(
                'SELECT user_id FROM user_info WHERE username = ? AND user_id != ?',
                [username, req.user.userId]
            );
            if (existingUsers.length > 0) {
                logger.warn('PUT /auth/update_profile - 用户名 \'%s\' 已被占用，用户 ID: %d 尝试更改。', username, req.user.userId);
                return res.status(409).json({ message: '用户名已被占用。' });
            }
            fieldsToUpdate.push('username = ?');
            values.push(username);
        }
        if (email !== undefined) {
            fieldsToUpdate.push('email = ?');
            values.push(email);
        }
        if (phone !== undefined) {
            fieldsToUpdate.push('phone = ?');
            values.push(phone);
        }
        if (real_name !== undefined) {
            fieldsToUpdate.push('real_name = ?');
            values.push(real_name);
        }
        if (id_type !== undefined) {
            fieldsToUpdate.push('id_type = ?');
            values.push(id_type);
        }
        if (id_number !== undefined) {
            fieldsToUpdate.push('id_number = ?');
            values.push(id_number);
        }
        if (driver_license !== undefined) {
            fieldsToUpdate.push('driver_license = ?');
            values.push(driver_license);
        }
        if (license_expire_date !== undefined) {
            fieldsToUpdate.push('license_expire_date = ?');
            values.push(license_expire_date);
        }
        if (emergency_contact !== undefined) {
            fieldsToUpdate.push('emergency_contact = ?');
            values.push(emergency_contact);
        }
        if (emergency_phone !== undefined) {
            fieldsToUpdate.push('emergency_phone = ?');
            values.push(emergency_phone);
        }
        if (credit_score !== undefined) {
            fieldsToUpdate.push('credit_score = ?');
            values.push(credit_score);
        }

        if (fieldsToUpdate.length === 0) {
            return res.status(400).json({ message: '没有有效的字段可供更新。' });
        }

        // 添加 update_time 字段更新
        fieldsToUpdate.push('update_time = CURRENT_TIMESTAMP');

        const query = `UPDATE user_info SET ${fieldsToUpdate.join(', ')} WHERE user_id = ?`;
        values.push(req.user.userId); // WHERE 子句的参数

        const [result] = await connection.execute(query, values);

        if (result.affectedRows === 0) {
            logger.warn('PUT /auth/update_profile - 用户 ID: %d 未找到或没有数据被更改。', req.user.userId);
            return res.status(404).json({ message: '用户未找到或未进行任何更改。' });
        }

        logger.info('PUT /auth/update_profile - 用户 ID: %d 个人资料更新成功。', req.user.userId);
        res.json({ message: '用户个人资料更新成功' });

    } catch (error) {
        logger.error('PUT /auth/update_profile - 更新用户 ID %d 个人资料时发生错误：%s', req.user.userId, error.stack);
        res.status(500).json({
            message: '服务器内部错误',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

module.exports = router;