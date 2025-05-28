// car-rental/src/axios.js
import axios from 'axios';
import router from './router'; // 【重要】确保导入 router 实例，用于页面跳转

// --- 1. Flask 后端 Axios 实例 ---
const flaskApiService = axios.create({
    baseURL: 'http://localhost:5000', // 你的 Flask 后端服务器地址
    timeout: 10000,
    withCredentials: true, // 允许携带 cookie，确保跨域请求时能发送 session cookie
});

// Flask 后端请求拦截器 (如果 Flask 需要特定的请求头或处理，可以在这里添加)
flaskApiService.interceptors.request.use(
    (config) => {
        // 例如，如果 Flask 也有自己的 Session ID 或 CSRF token 逻辑，可以在这里添加
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Flask 后端响应拦截器 (用于处理 Flask 返回的错误或数据格式)
flaskApiService.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // 这里可以针对 Flask 后端返回的错误进行处理
        console.error('Flask API 错误:', error.response || error);
        return Promise.reject(error);
    }
);

// --- 2. Node.js 后端 Axios 实例 ---
const nodeApiService = axios.create({
    baseURL: 'http://localhost:3000/api', // 你的 Node.js API 服务器地址
    timeout: 5000, // Node.js 服务可以设置更短的超时
    withCredentials: true, // 如果你的 Node.js CORS 配置允许 credentials
});

// Node.js 后端请求拦截器：添加 JWT
nodeApiService.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token'); // 从 localStorage 获取存储的 JWT

        // 检查请求的 URL 是否是登录或注册路径
        // config.url 是相对于 baseURL 的路径，例如 '/auth/login' 或 '/auth/register'
        const isAuthRoute = config.url === '/auth/login' || config.url === '/auth/register';

        // 只有当不是认证路由 且 令牌存在时，才添加 Authorization 头
        if (token && !isAuthRoute) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log(`Node.js API 请求拦截器：已添加 JWT 到 Authorization 头，请求路径: ${config.url}`);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Node.js 后端响应拦截器：处理 JWT 过期或无效等 Node.js 相关的错误
nodeApiService.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            const status = error.response.status;
            // 捕获 401 Unauthorized 或 403 Forbidden 错误
            if (status === 401 || status === 403) {
                console.error('Node.js API 错误: JWT 令牌已过期或无效。正在清除令牌并重定向到登录页。');
                // 清除无效的 JWT 和相关用户信息
                localStorage.removeItem('token');
                localStorage.removeItem('userId');
                localStorage.removeItem('username');

                // 如果路由实例已导入，且当前不在登录页，则跳转
                if (router && router.currentRoute.name !== 'Login') { // 【优化】使用 name 属性更稳健
                    router.push({ name: 'Login' }).catch(err => {
                        // 捕获 push 路由可能产生的导航冗余错误
                        if (err.name !== 'NavigationDuplicated') {
                            console.error('路由跳转到登录页失败:', err);
                        }
                    });
                    alert('您的会话已过期，请重新登录。'); // 提示用户
                } else {
                    // 如果已经在登录页，也给个提示，避免重复提示
                    alert('您的会话已过期，请重新登录。');
                }
            }
        }
        console.error('Node.js API 错误:', error.response || error);
        return Promise.reject(error);
    }
);

// --- 3. 导出两个实例 ---
export {
    flaskApiService, // 导出用于 Flask 后端的实例
    nodeApiService   // 导出用于 Node.js 后端的实例
};