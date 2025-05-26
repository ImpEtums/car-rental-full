// node-service/src/api/auth.js

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs'); // 确保使用 bcryptjs
const dbPool = require('../config/db');
const logger = require('../config/log');

const router = express.Router();

// 确保 JWT_SECRET 在主入口文件加载 .env 后可用
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRES_IN = '1h'; // JWT 有效期

// --- JWT 鉴权中间件 ---
// 这个中间件现在被定义在当前文件，并将在 app.js 中导入使用。
// 不再是 router.authenticateToken，而是作为一个独立的函数。
const authenticateToken = (req, res, next) => {
    logger.debug('Attempting to authenticate token for %s %s', req.method, req.url);
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token == null) {
        logger.warn('No token provided for %s %s', req.method, req.url);
        return res.status(401).json({ message: 'Unauthorized: No token provided' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            logger.error('Token verification failed for %s %s: %s', req.method, req.url, err.message);
            if (err.name === 'TokenExpiredError') {
                return res.status(401).json({ message: 'Forbidden: Token expired', error: err.message });
            }
            return res.status(403).json({ message: 'Forbidden: Invalid token', error: err.message });
        }
        req.user = user; // 将解码后的用户信息（userId, username）存储在请求对象中
        logger.info('Token authenticated for user ID: %d (Username: %s)', user.userId, user.username);
        next();
    });
};

// --- 用户注册 API (POST /api/auth/register) ---
router.post('/register', async (req, res) => {
    const { username, email, password, real_name, phone, id_number } = req.body;
    logger.info('User registration attempt for username: %s', username);

    if (!username || !email || !password || !real_name || !phone || !id_number) {
        logger.warn('Registration attempt with missing required fields.');
        return res.status(400).json({ message: '所有注册字段都是必需的' });
    }

    let connection;
    try {
        connection = await dbPool.getConnection();

        const [existingUsers] = await connection.execute(
            'SELECT user_id FROM user_info WHERE username = ? OR email = ? OR phone = ? OR id_number = ?',
            [username, email, phone, id_number]
        );

        if (existingUsers.length > 0) {
            logger.warn('Registration attempt for existing user data.');
            return res.status(409).json({ message: '用户名、邮箱、手机号或身份证号已被注册' });
        }

        const saltRounds = 10;
        const hashedPassword = await bcrypt.hash(password, saltRounds);
        logger.debug('Hashed password for %s generated.', username);

        const [result] = await connection.execute(
            'INSERT INTO user_info (username, email, password, real_name, phone, id_number) VALUES (?, ?, ?, ?, ?, ?)',
            [username, email, hashedPassword, real_name, phone, id_number]
        );

        logger.info('User %s (ID: %d) registered successfully.', username, result.insertId);
        res.status(201).json({ message: 'User registered successfully', userId: result.insertId });

    } catch (error) {
        logger.error('Error during user registration for %s: %s', username, error.stack);
        res.status(500).json({
            message: 'Internal server error',
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
    logger.info('User login attempt for username: %s', username);

    if (!username || !password) {
        logger.warn('Login attempt with missing username or password.');
        return res.status(400).json({ message: 'Username and password are required' });
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
            logger.warn('Login attempt: User %s not found.', username);
            return res.status(401).json({ message: '用户名或密码不正确' });
        }

        const isMatch = await bcrypt.compare(password, user.password);

        if (!isMatch) {
            logger.warn('Login attempt: Password mismatch for user %s.', username);
            return res.status(401).json({ message: '用户名或密码不正确' });
        }

        const token = jwt.sign(
            { userId: user.user_id, username: user.username },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
        );

        logger.info('User %s (ID: %d) logged in successfully. Token issued.', user.username, user.user_id);
        res.json({
            message: 'Login successful',
            token: token,
            userId: user.user_id,
            username: user.username
        });

    } catch (error) {
        logger.error('Error during user login for %s: %s', username, error.stack);
        res.status(500).json({
            message: 'Internal server error',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

// --- 获取当前登录用户的信息 API (GET /api/auth/me) ---
// 使用我们定义的 authenticateToken 中间件来保护此路由
router.get('/me', authenticateToken, async (req, res) => {
    // authenticateToken 中间件会将解码后的用户信息（userId, username）放入 req.user
    logger.info('GET /auth/me - Fetching profile for user ID: %d, Username: %s', req.user.userId, req.user.username);

    let connection;
    try {
        connection = await dbPool.getConnection();
        // 从数据库获取更详细的用户信息，但不包括密码
        const [rows] = await connection.execute(
            // *** 关键修改 1: 表名改为 user_info ***
            // *** 关键修改 2: created_at 改为 register_time ***
            // *** 关键修改 3: 确保 SELECT 的列与你的 user_info 表完全匹配，且是你需要返回的 ***
            // 我这里列出了你 DESCRIBE user_info 结果中的大部分字段，请根据实际需要进行调整
            'SELECT user_id, username, email, real_name, id_type, id_number, phone, register_time, driver_license, license_expire_date, emergency_contact, emergency_phone, credit_score FROM user_info WHERE user_id = ?',
            [req.user.userId] // 使用 Token 中解码出的 userId
        );

        if (rows.length === 0) {
            logger.warn('GET /auth/me - Profile not found for user ID: %d', req.user.userId);
            return res.status(404).json({ message: 'User profile not found' });
        }

        const userProfile = rows[0];
        res.json({
            message: 'User profile fetched successfully',
            user: {
                userId: userProfile.user_id,
                username: userProfile.username,
                email: userProfile.email,
                realName: userProfile.real_name, // 注意这里是 camelCase
                phone: userProfile.phone,
                idNumber: userProfile.id_number, // 注意这里是 camelCase
                // *** 关键修改 4: 将返回给前端的键名从 created_at 改为 registerTime (或 register_time) ***
                // 推荐改为 camelCase，与前端保持一致
                registerTime: userProfile.register_time 
                // 其他你可能需要的字段，例如：
                // driverLicense: userProfile.driver_license,
                // licenseExpireDate: userProfile.license_expire_date,
                // emergencyContact: userProfile.emergency_contact,
                // emergencyPhone: userProfile.emergency_phone,
                // creditScore: userProfile.credit_score
            }
        });

    } catch (error) {
        logger.error('GET /auth/me - Error fetching user profile for ID %d: %s', req.user.userId, error.stack);
        res.status(500).json({
            message: 'Internal server error',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

// --- 更新用户个人信息 API (PUT /api/auth/update_profile) ---
// 使用我们定义的 authenticateToken 中间件来保护此路由
router.put('/update_profile', authenticateToken, async (req, res) => {
    logger.info('PUT /auth/update_profile - Attempting to update profile for user ID: %d, Username: %s', req.user.userId, req.user.username);
    const { username, email, phone } = req.body; // 从请求体获取要更新的字段

    // 可以在这里添加输入验证 (例如，确保邮箱格式正确，手机号是数字等)
    if (!username || !email || !phone) {
        logger.warn('PUT /auth/update_profile - Missing required fields for user ID: %d', req.user.userId);
        return res.status(400).json({ message: 'Username, email, and phone are required.' });
    }

    let connection;
    try {
        connection = await dbPool.getConnection();

        // 检查更新后的用户名是否已存在 (除了当前用户自己)
        const [existingUsers] = await connection.execute(
            'SELECT user_id FROM user_info WHERE username = ? AND user_id != ?',
            [username, req.user.userId]
        );

        if (existingUsers.length > 0) {
            logger.warn('PUT /auth/update_profile - Username already exists for user ID: %d, trying to change to: %s', req.user.userId, username);
            return res.status(409).json({ message: 'Username already taken.' });
        }

        const [result] = await connection.execute(
            'UPDATE user_info SET username = ?, email = ?, phone = ?, update_time = CURRENT_TIMESTAMP WHERE user_id = ?',
            [username, email, phone, req.user.userId]
        );

        if (result.affectedRows === 0) {
            logger.warn('PUT /auth/update_profile - No rows affected for user ID: %d. User might not exist or no changes were made.', req.user.userId);
            return res.status(404).json({ message: 'User not found or no changes provided.' });
        }

        logger.info('PUT /auth/update_profile - User profile updated successfully for user ID: %d', req.user.userId);
        res.json({ message: 'User profile updated successfully' });

    } catch (error) {
        logger.error('PUT /auth/update_profile - Error updating user profile for ID %d: %s', req.user.userId, error.stack);
        res.status(500).json({
            message: 'Internal server error',
            detailedError: error.message,
            stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
    } finally {
        if (connection) connection.release();
    }
});

module.exports = router;