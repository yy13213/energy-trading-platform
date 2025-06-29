#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源交易平台并发测试脚本
测试目标：并发用户数 > 200
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
import csv
import os
from concurrent.futures import ThreadPoolExecutor
import threading

class ConcurrentTest:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.results = []
        self.active_users = 0
        self.max_concurrent_users = 0
        self.test_token = "test_token_for_concurrent_testing"
        self.lock = threading.Lock()
        
    async def simulate_user_session(self, session, user_id, session_duration=30):
        """模拟单个用户会话"""
        with self.lock:
            self.active_users += 1
            if self.active_users > self.max_concurrent_users:
                self.max_concurrent_users = self.active_users
        
        try:
            start_time = time.time()
            session_results = []
            
            # 用户操作序列 - 使用不需要认证的接口
            user_actions = [
                ('/cache_stats', 'GET', {}),
                ('/getAvailableEnergy', 'POST', {}),
                ('/get_items', 'POST', {}),
                ('/getUserAvailableEnergy', 'POST', {'user_address': f'test_user_{user_id}'}),
                ('/log_page_visit', 'POST', {'page': f'test_page_{user_id}', 'user_agent': 'test_agent'}),
            ]
            
            # 在会话期间重复执行操作
            while time.time() - start_time < session_duration:
                for endpoint, method, data in user_actions:
                    try:
                        result = await self.make_request(session, endpoint, method, data, user_id)
                        session_results.append(result)
                        
                        # 模拟用户思考时间
                        await asyncio.sleep(0.1 + (user_id % 5) * 0.1)  # 0.1-0.6秒随机间隔
                        
                    except Exception as e:
                        session_results.append({
                            'user_id': user_id,
                            'endpoint': endpoint,
                            'method': method,
                            'response_time': 0,
                            'status': 0,
                            'success': False,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })
            
            return session_results
            
        finally:
            with self.lock:
                self.active_users -= 1
    
    async def make_request(self, session, endpoint, method, data, user_id):
        """发送HTTP请求"""
        # 大部分接口不需要认证，只设置基本headers
        headers = {'Content-Type': 'application/json'}
        
        start_time = time.time()
        try:
            if method.upper() == "POST":
                async with session.post(f"{self.base_url}{endpoint}", 
                                      json=data, 
                                      headers=headers) as response:
                    await response.text()
                    status = response.status
            else:
                async with session.get(f"{self.base_url}{endpoint}", 
                                     headers=headers) as response:
                    await response.text()
                    status = response.status
                    
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'user_id': user_id,
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'status': status,
                'success': status < 400,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                'user_id': user_id,
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'status': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_concurrent_test(self, target_users=250, ramp_up_time=30, test_duration=120):
        """运行并发测试"""
        print(f"🚀 开始并发测试...")
        print(f"📊 测试参数:")
        print(f"   目标并发用户数: {target_users}")
        print(f"   爬坡时间: {ramp_up_time}秒")
        print(f"   测试持续时间: {test_duration}秒")
        
        # 配置连接池
        connector = aiohttp.TCPConnector(
            limit=target_users + 50,  # 连接池大小
            limit_per_host=target_users + 50,
            ttl_dns_cache=300
        )
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            
            tasks = []
            start_time = time.time()
            
            # 阶段1: 爬坡阶段 - 逐渐增加用户
            print(f"📈 阶段1: 爬坡阶段 ({ramp_up_time}秒)")
            for i in range(target_users):
                # 计算用户启动时间
                user_start_delay = (i / target_users) * ramp_up_time
                
                # 创建用户会话任务
                task = asyncio.create_task(
                    self.delayed_user_session(session, i, user_start_delay, test_duration)
                )
                tasks.append(task)
                
                # 实时显示进度
                if i % 50 == 0:
                    print(f"   已创建 {i} 个用户任务...")
            
            print(f"✅ 所有 {target_users} 个用户任务已创建")
            
            # 阶段2: 监控阶段
            print(f"📊 阶段2: 监控阶段")
            monitor_interval = 5  # 每5秒监控一次
            total_test_time = ramp_up_time + test_duration
            
            while time.time() - start_time < total_test_time:
                await asyncio.sleep(monitor_interval)
                elapsed = time.time() - start_time
                print(f"   时间: {elapsed:.1f}s | 当前并发用户: {self.active_users} | 峰值并发: {self.max_concurrent_users}")
            
            # 阶段3: 等待所有任务完成
            print(f"⏳ 阶段3: 等待所有用户会话结束...")
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 收集所有结果
            for user_results in all_results:
                if isinstance(user_results, list):
                    self.results.extend(user_results)
                elif isinstance(user_results, dict):
                    self.results.append(user_results)
        
        print(f"✅ 并发测试完成")
        print(f"   峰值并发用户数: {self.max_concurrent_users}")
        print(f"   收集到的请求数: {len(self.results)}")
    
    async def delayed_user_session(self, session, user_id, delay, duration):
        """延迟启动的用户会话"""
        # 等待到指定的启动时间
        await asyncio.sleep(delay)
        
        # 开始用户会话
        return await self.simulate_user_session(session, user_id, duration)
    
    def analyze_concurrent_results(self):
        """分析并发测试结果"""
        if not self.results:
            print("❌ 没有测试结果可分析")
            return None
        
        # 基础统计
        successful_requests = [r for r in self.results if r.get('success', False)]
        failed_requests = [r for r in self.results if not r.get('success', False)]
        
        if not successful_requests:
            print("❌ 没有成功的请求")
            return None
        
        # 响应时间统计
        response_times = [r['response_time'] for r in successful_requests]
        
        # 并发用户统计
        unique_users = len(set(r.get('user_id', 0) for r in self.results))
        
        # 按时间段分析并发度
        time_buckets = {}
        for result in self.results:
            timestamp = result.get('timestamp', '')
            if timestamp:
                # 按分钟分组
                minute_key = timestamp[:16]  # YYYY-MM-DDTHH:MM
                if minute_key not in time_buckets:
                    time_buckets[minute_key] = set()
                time_buckets[minute_key].add(result.get('user_id', 0))
        
        # 计算每分钟的并发用户数
        concurrent_users_per_minute = {k: len(v) for k, v in time_buckets.items()}
        avg_concurrent_users = statistics.mean(concurrent_users_per_minute.values()) if concurrent_users_per_minute else 0
        
        analysis = {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'unique_users': unique_users,
            'max_concurrent_users': self.max_concurrent_users,
            'avg_concurrent_users': avg_concurrent_users,
            'average_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': self.percentile(response_times, 95),
            'p99_response_time': self.percentile(response_times, 99),
            'concurrent_users_per_minute': concurrent_users_per_minute
        }
        
        # 按端点分析
        endpoint_stats = {}
        for result in successful_requests:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = []
            endpoint_stats[endpoint].append(result['response_time'])
        
        analysis['endpoint_stats'] = {}
        for endpoint, times in endpoint_stats.items():
            analysis['endpoint_stats'][endpoint] = {
                'count': len(times),
                'average': statistics.mean(times),
                'min': min(times),
                'max': max(times)
            }
        
        return analysis
    
    def percentile(self, data, percentile):
        """计算百分位数"""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def generate_concurrent_report(self, analysis, output_file="concurrent_report.md"):
        """生成并发测试报告"""
        if not analysis:
            return
        
        report_content = f"""# 🚀 能源交易平台并发测试报告

## 📊 测试概览

- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试目标**: 并发用户数 > 200
- **实际峰值并发用户数**: {analysis['max_concurrent_users']}
- **平均并发用户数**: {analysis['avg_concurrent_users']:.1f}
- **总请求数**: {analysis['total_requests']}
- **成功请求数**: {analysis['successful_requests']}
- **失败请求数**: {analysis['failed_requests']}
- **成功率**: {analysis['success_rate']:.2f}%

## 🎯 并发性能指标

| 指标 | 数值 | 目标 | 状态 |
|------|------|------|------|
| 峰值并发用户数 | {analysis['max_concurrent_users']} | > 200 | {'✅ 通过' if analysis['max_concurrent_users'] > 200 else '❌ 未通过'} |
| 平均并发用户数 | {analysis['avg_concurrent_users']:.1f} | - | - |
| 总用户数 | {analysis['unique_users']} | - | - |
| 系统成功率 | {analysis['success_rate']:.2f}% | > 95% | {'✅ 良好' if analysis['success_rate'] > 95 else '⚠️ 需要改进'} |

## ⏱️ 高并发下的响应时间

| 指标 | 数值 | 状态 |
|------|------|------|
| 平均响应时间 | {analysis['average_response_time']:.3f}s | {'✅ 良好' if analysis['average_response_time'] < 5 else '⚠️ 需要优化'} |
| 中位数响应时间 | {analysis['median_response_time']:.3f}s | - |
| 最小响应时间 | {analysis['min_response_time']:.3f}s | - |
| 最大响应时间 | {analysis['max_response_time']:.3f}s | {'✅ 可接受' if analysis['max_response_time'] < 30 else '❌ 过长'} |
| P95响应时间 | {analysis['p95_response_time']:.3f}s | {'✅ 良好' if analysis['p95_response_time'] < 10 else '⚠️ 需要优化'} |
| P99响应时间 | {analysis['p99_response_time']:.3f}s | {'✅ 良好' if analysis['p99_response_time'] < 15 else '⚠️ 需要优化'} |

## 📈 各端点并发性能

| 端点 | 请求数 | 平均响应时间 | 最小时间 | 最大时间 | 状态 |
|------|--------|--------------|----------|----------|------|
"""
        
        for endpoint, stats in analysis['endpoint_stats'].items():
            status = '✅ 良好' if stats['average'] < 5 else ('⚠️ 一般' if stats['average'] < 10 else '❌ 较慢')
            report_content += f"| {endpoint} | {stats['count']} | {stats['average']:.3f}s | {stats['min']:.3f}s | {stats['max']:.3f}s | {status} |\n"
        
        # 并发用户数时间分布
        if analysis['concurrent_users_per_minute']:
            report_content += f"""
## 📊 并发用户数时间分布

| 时间点 | 并发用户数 |
|--------|------------|
"""
            for time_point, user_count in sorted(analysis['concurrent_users_per_minute'].items()):
                report_content += f"| {time_point} | {user_count} |\n"
        
        report_content += f"""
## 🎯 测试结论

### 并发目标达成情况
- **并发用户数目标**: {'✅ 达成' if analysis['max_concurrent_users'] > 200 else '❌ 未达成'}
- **系统稳定性**: {'✅ 良好' if analysis['success_rate'] > 95 else '⚠️ 需要改进'}
- **响应性能**: {'✅ 良好' if analysis['average_response_time'] < 5 else '⚠️ 需要优化'}

### 性能评估
"""
        
        if analysis['max_concurrent_users'] <= 200:
            report_content += "- ❌ 未达到200并发用户目标，建议优化服务器配置和数据库连接池\n"
        else:
            report_content += f"- ✅ 成功支持 {analysis['max_concurrent_users']} 并发用户\n"
        
        if analysis['success_rate'] < 95:
            report_content += "- ⚠️ 高并发下成功率低于95%，建议检查错误处理和资源限制\n"
        
        if analysis['average_response_time'] > 5:
            report_content += "- ⚠️ 高并发下平均响应时间过长，建议优化数据库查询和缓存策略\n"
        
        if analysis['max_response_time'] > 30:
            report_content += "- ⚠️ 最大响应时间过长，建议添加请求超时和负载均衡\n"
        
        if (analysis['max_concurrent_users'] > 200 and 
            analysis['success_rate'] > 95 and 
            analysis['average_response_time'] < 5):
            report_content += "- ✅ 系统并发性能表现优秀，满足高并发要求\n"
        
        report_content += f"""
## 📝 详细数据

### 测试配置
- 目标并发用户数: > 200
- 实际测试用户数: {analysis['unique_users']}
- 峰值并发用户数: {analysis['max_concurrent_users']}
- 总请求数: {analysis['total_requests']}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        os.makedirs('tests/reports', exist_ok=True)
        report_path = f"tests/reports/{output_file}"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 并发测试报告已生成: {report_path}")
        return report_path
    
    def save_concurrent_raw_data(self, filename="concurrent_raw_data.csv"):
        """保存原始并发测试数据"""
        os.makedirs('tests/reports', exist_ok=True)
        csv_path = f"tests/reports/{filename}"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'user_id', 'endpoint', 'method', 'response_time', 'status', 'success']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    'timestamp': result.get('timestamp', ''),
                    'user_id': result.get('user_id', ''),
                    'endpoint': result.get('endpoint', ''),
                    'method': result.get('method', ''),
                    'response_time': result.get('response_time', 0),
                    'status': result.get('status', 0),
                    'success': result.get('success', False)
                })
        
        print(f"💾 原始并发数据已保存: {csv_path}")

async def main():
    """主函数"""
    print("🎯 能源交易平台并发测试")
    print("=" * 50)
    
    tester = ConcurrentTest()
    
    # 运行并发测试 (目标250用户，30秒爬坡，120秒测试)
    await tester.run_concurrent_test(
        target_users=250, 
        ramp_up_time=30, 
        test_duration=120
    )
    
    # 分析结果
    analysis = tester.analyze_concurrent_results()
    
    if analysis:
        # 生成报告
        tester.generate_concurrent_report(analysis)
        tester.save_concurrent_raw_data()
        
        # 打印关键指标
        print("\n📊 关键并发指标:")
        print(f"   峰值并发用户数: {analysis['max_concurrent_users']}")
        print(f"   平均并发用户数: {analysis['avg_concurrent_users']:.1f}")
        print(f"   成功率: {analysis['success_rate']:.2f}%")
        print(f"   平均响应时间: {analysis['average_response_time']:.3f}s")
        
        # 检查是否达到目标
        if analysis['max_concurrent_users'] > 200:
            print("   ✅ 并发目标达成！")
        else:
            print("   ❌ 并发目标未达成")

if __name__ == "__main__":
    asyncio.run(main()) 