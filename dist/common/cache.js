// 前端缓存系统，提升页面加载速度
class APICache {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30秒过期
        this.pendingRequests = new Map(); // 避免重复请求
    }

    // 生成缓存键
    getCacheKey(url, data) {
        return url + JSON.stringify(data || {});
    }

    // 检查缓存是否有效
    isValid(cacheItem) {
        return Date.now() - cacheItem.timestamp < this.cacheTimeout;
    }

    // 获取缓存或发起请求
    async get(url, data = {}, config = {}) {
        const cacheKey = this.getCacheKey(url, data);
        
        // 检查缓存
        if (this.cache.has(cacheKey)) {
            const cacheItem = this.cache.get(cacheKey);
            if (this.isValid(cacheItem)) {
                console.log('📋 使用缓存数据:', url);
                return Promise.resolve(cacheItem.data);
            }
        }

        // 检查是否有进行中的请求
        if (this.pendingRequests.has(cacheKey)) {
            console.log('⏳ 等待进行中的请求:', url);
            return this.pendingRequests.get(cacheKey);
        }

        // 发起新请求
        console.log('🌐 发起新请求:', url);
        const requestPromise = axios.post(url, data, config)
            .then(response => {
                // 缓存结果
                this.cache.set(cacheKey, {
                    data: response,
                    timestamp: Date.now()
                });
                
                // 清除进行中的请求
                this.pendingRequests.delete(cacheKey);
                
                return response;
            })
            .catch(error => {
                // 清除进行中的请求
                this.pendingRequests.delete(cacheKey);
                throw error;
            });

        // 记录进行中的请求
        this.pendingRequests.set(cacheKey, requestPromise);
        
        return requestPromise;
    }

    // 清除缓存
    clear() {
        this.cache.clear();
        this.pendingRequests.clear();
    }

    // 清除特定URL的缓存
    clearUrl(url) {
        for (let key of this.cache.keys()) {
            if (key.startsWith(url)) {
                this.cache.delete(key);
            }
        }
    }
}

// 全局缓存实例
window.apiCache = new APICache();

// 通用的API请求函数
window.cachedRequest = function(url, data = {}) {
    const token = localStorage.getItem('token');
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': ` ${token}`,
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    return window.apiCache.get(url, data, config);
};

// 页面隐藏时清除缓存，释放内存
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        setTimeout(() => {
            if (document.hidden) {
                window.apiCache.clear();
                console.log('🧹 页面隐藏，清除缓存');
            }
        }, 60000); // 1分钟后清除
    }
}); 