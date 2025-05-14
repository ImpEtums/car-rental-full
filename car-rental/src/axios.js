import axios from 'axios';

// 创建 Axios 实例
const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000',  // 后端服务器地址
    timeout: 10000,  // 设置请求超时
    withCredentials: true,  // 允许携带 cookie，确保跨域请求时能发送 session cookie
});

// 可以在这里配置请求拦截器（如添加 token）或响应拦截器
axiosInstance.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default axiosInstance;
