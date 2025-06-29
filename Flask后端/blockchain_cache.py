# 区块链缓存模块 - 大幅提升性能
import time
import json
from functools import wraps
import common_utils

class BlockchainCache:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 15  # 15秒缓存过期（区块链数据更新较慢）
        self.hit_count = 0
        self.miss_count = 0
        self.total_time_saved = 0.0  # 缓存节省的总时间（毫秒）
        self.avg_blockchain_time = 2200.0  # 平均区块链调用时间（毫秒）
        
    def get_cache_key(self, user_address, contract_name, func_name, func_inputs):
        """生成缓存键"""
        # 标准化参数格式，确保缓存键一致性
        inputs_str = str(sorted(func_inputs) if isinstance(func_inputs, list) else func_inputs)
        cache_key = f"{user_address}:{contract_name}:{func_name}:{inputs_str}"
        return cache_key
    
    def is_cache_valid(self, cache_item):
        """检查缓存是否有效"""
        return time.time() - cache_item['timestamp'] < self.cache_timeout
    
    def get_cached_result(self, user_address, contract_name, func_name, func_inputs, contract_address, contract_abi):
        """获取缓存结果或执行区块链调用"""
        cache_key = self.get_cache_key(user_address, contract_name, func_name, func_inputs)
        
        # 检查缓存
        if cache_key in self.cache:
            cache_item = self.cache[cache_key]
            if self.is_cache_valid(cache_item):
                self.hit_count += 1
                self.total_time_saved += self.avg_blockchain_time
                hit_rate = (self.hit_count / (self.hit_count + self.miss_count)) * 100
                print(f"⚡ 缓存命中: {func_name} | 命中率: {hit_rate:.1f}% | 已节省: {self.total_time_saved/1000:.1f}s")
                return cache_item['result']
            else:
                # 缓存过期，删除旧缓存
                del self.cache[cache_key]
                print(f"🕒 缓存过期: {func_name}")
        
        # 缓存未命中，执行区块链调用
        self.miss_count += 1
        print(f"🌐 新区块链请求: {func_name} | 缓存: {len(self.cache)}项")
        
        result = common_utils.common_bc_req(user_address, contract_name, func_name, func_inputs, contract_address, contract_abi)
        
        # 缓存结果
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        return result
    
    def clear_cache(self):
        """清除所有缓存"""
        self.cache.clear()
        print("🧹 区块链缓存已清除")
    
    def get_cache_stats(self):
        """获取缓存统计信息"""
        total_calls = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_calls * 100) if total_calls > 0 else 0
        return {
            'total_calls': total_calls,
            'cache_hits': self.hit_count,
            'cache_misses': self.miss_count,
            'hit_rate': hit_rate,
            'time_saved_seconds': self.total_time_saved / 1000,
            'cache_size': len(self.cache)
        }
    
    def clear_expired_cache(self):
        """清除过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, cache_item in self.cache.items():
            if current_time - cache_item['timestamp'] >= self.cache_timeout:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"🧹 清除{len(expired_keys)}个过期区块链缓存")

# 全局缓存实例
blockchain_cache = BlockchainCache()

def cached_blockchain_call(user_address, contract_name, func_name, func_inputs, contract_address, contract_abi):
    """缓存的区块链调用函数"""
    return blockchain_cache.get_cached_result(user_address, contract_name, func_name, func_inputs, contract_address, contract_abi)

# 定期清理过期缓存的装饰器
def auto_cleanup_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 每10次调用清理一次过期缓存
        if not hasattr(wrapper, 'call_count'):
            wrapper.call_count = 0
        wrapper.call_count += 1
        
        if wrapper.call_count % 10 == 0:
            blockchain_cache.clear_expired_cache()
        
        return func(*args, **kwargs)
    return wrapper 