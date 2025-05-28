// node-api/controllers/authController.js
// ... (其他导入和 login/register 函数)

const getMe = async (req, res) => {
    let connection;
    try {
        const userId = req.user.userId;
        // 确认这些 DEBUG 日志存在
        console.log(`DEBUG: getMe 函数接收到的 userId: ${userId}`);
        logger.debug(`DEBUG: getMe 函数接收到的 userId: ${userId}`);

        if (!userId) {
            logger.warn('获取个人信息：未提供用户ID (可能未认证)。');
            return res.status(401).json({ message: '未授权：请先登录。' });
        }

        connection = await pool.getConnection();

        const [rows] = await connection.execute(
            'SELECT user_id, username, email, real_name, id_number, phone, register_time, driver_license, license_expire_date, emergency_contact, emergency_phone, credit_score FROM user_info WHERE user_id = ?',
            [userId]
        );

        // 确认这些 DEBUG 日志存在
        console.log('DEBUG: 数据库查询返回的 rows:', rows);
        logger.debug('DEBUG: 数据库查询返回的 rows:', rows);

        const user = rows[0];
        // 确认这些 DEBUG 日志存在
        console.log('DEBUG: 从 rows[0] 获取到的 user 对象:', user);
        logger.debug('DEBUG: 从 rows[0] 获取到的 user 对象:', user);

        if (!user) {
            logger.warn(`获取个人信息：用户 ID ${userId} 未找到。`);
            return res.status(404).json({ message: '用户信息未找到。' });
        }

        logger.info(`用户 ID ${userId} 个人信息获取成功。`);

        res.status(200).json({
            message: '获取用户信息成功',
            user: {
                userId: user.user_id,
                username: user.username,
                email: user.email,
                realName: user.real_name,
                idNumber: user.id_number,
                phone: user.phone,
                // *** 关键修改：直接使用 'registerTime' 匹配前端实际收到的字段名 ***
                registerTime: user.register_time, // 数据库字段是 register_time，返回给前端命名为 registerTime
                // 根据您数据库中有的字段，这里也需要将它们包含进来，确保前端能收到
                driverLicense: user.driver_license,
                licenseExpireDate: user.license_expire_date,
                emergencyContact: user.emergency_contact,
                emergencyPhone: user.emergency_phone,
                creditScore: user.credit_score
            }
        });

    } catch (error) {
        // 确认这个错误日志存在
        console.error('ERROR: 获取个人信息过程中发生错误:', error);
        logger.error(`获取个人信息过程中发生错误：${error.message}`, error);
        res.status(500).json({ message: '服务器内部错误，无法获取个人信息。' });
    } finally {
        if (connection) connection.release();
    }
};

module.exports = {
    login,
    register,
    getMe
};