#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源交易平台性能测试脚本
测试目标：平均响应时间 < 3秒
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
import csv
import os

class PerformanceTest:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.results = []
        self.test_token = None
        
    async def login_and_get_token(self, session):
        """登录获取测试token"""
        try:
            login_data = {
                "username": "test_user",
                "password": "test_password"
            }
            
            async with session.post(f"{self.base_url}/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_token = data.get('token', 'test_token')
                    print(f"✅ 登录成功，获取token: {self.test_token[:20]}...")
                else:
                    # 如果登录失败，使用默认token进行测试
                    self.test_token = "test_token_for_performance_testing"
                    print(f"⚠️ 登录失败，使用默认token进行测试")
        except Exception as e:
            print(f"⚠️ 登录异常: {e}，使用默认token")
            self.test_token = "test_token_for_performance_testing"
    
    async def test_single_request(self, session, endpoint, method="POST", data=None):
        """测试单个请求的响应时间"""
        # 根据端点决定是否需要认证
        auth_required_endpoints = ['/test_energy_data']
        
        headers = {'Content-Type': 'application/json'}
        if endpoint in auth_required_endpoints:
            headers['Authorization'] = self.test_token
        
        # 为不同端点准备合适的测试数据
        test_data = data or {}
        if endpoint == '/log_page_visit':
            test_data = {'page': 'test_page', 'user_agent': 'test_agent'}
        elif endpoint == '/add_user_energy':
            test_data = {'user_address': 'test_address', 'amount': 100}
        elif endpoint == '/getUserAvailableEnergy':
            test_data = {'user_address': 'test_address'}
        
        start_time = time.time()
        try:
            if method.upper() == "POST":
                async with session.post(f"{self.base_url}{endpoint}", 
                                      json=test_data, 
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
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'status': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_performance_test(self, test_duration=60, concurrent_requests=50):
        """运行性能测试"""
        print(f"🚀 开始性能测试...")
        print(f"📊 测试参数: 持续时间={test_duration}秒, 并发请求={concurrent_requests}")
        
        # 测试的API端点 - 混合需要认证和不需要认证的接口
        test_endpoints = [
            ('/cache_stats', 'GET'),  # 不需要认证
            ('/getAvailableEnergy', 'POST'),  # 不需要认证
            ('/get_items', 'POST'),  # 不需要认证
            ('/getUserAvailableEnergy', 'POST'),  # 不需要认证
            ('/add_user_energy', 'POST'),  # 不需要认证
            ('/log_page_visit', 'POST'),  # 不需要认证
            ('/test_energy_data', 'POST'),  # 需要认证，测试认证机制
        ]
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            connector=aiohttp.TCPConnector(limit=200)
        ) as session:
            # 先登录获取token
            await self.login_and_get_token(session)
            
            start_time = time.time()
            tasks = []
            
            # 创建并发任务
            while time.time() - start_time < test_duration:
                for endpoint, method in test_endpoints:
                    if len(tasks) < concurrent_requests:
                        task = asyncio.create_task(
                            self.test_single_request(session, endpoint, method)
                        )
                        tasks.append(task)
                
                # 如果任务数达到并发限制，等待一些完成
                if len(tasks) >= concurrent_requests:
                    done, pending = await asyncio.wait(
                        tasks, 
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=1.0
                    )
                    
                    # 收集完成的结果
                    for task in done:
                        result = await task
                        self.results.append(result)
                    
                    # 更新任务列表
                    tasks = list(pending)
            
            # 等待剩余任务完成
            if tasks:
                remaining_results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in remaining_results:
                    if isinstance(result, dict):
                        self.results.append(result)
        
        print(f"✅ 性能测试完成，共收集 {len(self.results)} 个请求结果")
    
    def analyze_results(self):
        """分析测试结果"""
        if not self.results:
            print("❌ 没有测试结果可分析")
            return None
        
        # 过滤成功的请求
        successful_requests = [r for r in self.results if r.get('success', False)]
        failed_requests = [r for r in self.results if not r.get('success', False)]
        
        if not successful_requests:
            print("❌ 没有成功的请求")
            return None
        
        # 计算响应时间统计
        response_times = [r['response_time'] for r in successful_requests]
        
        analysis = {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'average_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': self.percentile(response_times, 95),
            'p99_response_time': self.percentile(response_times, 99),
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
    
    def generate_report(self, analysis, output_file="performance_report.md"):
        """生成测试报告"""
        if not analysis:
            return
        
        report_content = f"""# 🚀 能源交易平台性能测试报告

## 📊 测试概览

- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试目标**: 平均响应时间 < 3秒
- **总请求数**: {analysis['total_requests']}
- **成功请求数**: {analysis['successful_requests']}
- **失败请求数**: {analysis['failed_requests']}
- **成功率**: {analysis['success_rate']:.2f}%

## ⏱️ 响应时间统计

| 指标 | 数值 | 目标 | 状态 |
|------|------|------|------|
| 平均响应时间 | {analysis['average_response_time']:.3f}s | < 3s | {'✅ 通过' if analysis['average_response_time'] < 3 else '❌ 未通过'} |
| 中位数响应时间 | {analysis['median_response_time']:.3f}s | - | - |
| 最小响应时间 | {analysis['min_response_time']:.3f}s | - | - |
| 最大响应时间 | {analysis['max_response_time']:.3f}s | - | - |
| P95响应时间 | {analysis['p95_response_time']:.3f}s | - | - |
| P99响应时间 | {analysis['p99_response_time']:.3f}s | - | - |

## 📈 各端点性能分析

| 端点 | 请求数 | 平均响应时间 | 最小时间 | 最大时间 | 状态 |
|------|--------|--------------|----------|----------|------|
"""
        
        for endpoint, stats in analysis['endpoint_stats'].items():
            status = '✅ 良好' if stats['average'] < 3 else ('⚠️ 一般' if stats['average'] < 5 else '❌ 较慢')
            report_content += f"| {endpoint} | {stats['count']} | {stats['average']:.3f}s | {stats['min']:.3f}s | {stats['max']:.3f}s | {status} |\n"
        
        report_content += f"""
## 🎯 测试结论

### 性能目标达成情况
- **平均响应时间目标**: {'✅ 达成' if analysis['average_response_time'] < 3 else '❌ 未达成'}
- **系统稳定性**: {'✅ 良好' if analysis['success_rate'] > 95 else '⚠️ 需要改进'}

### 建议
"""
        
        if analysis['average_response_time'] >= 3:
            report_content += "- ⚠️ 平均响应时间超过3秒，建议优化数据库查询和缓存策略\n"
        
        if analysis['success_rate'] < 95:
            report_content += "- ⚠️ 成功率低于95%，建议检查错误处理和系统稳定性\n"
        
        if analysis['max_response_time'] > 10:
            report_content += "- ⚠️ 最大响应时间过长，建议添加请求超时处理\n"
        
        if analysis['average_response_time'] < 3 and analysis['success_rate'] > 95:
            report_content += "- ✅ 系统性能表现良好，满足性能要求\n"
        
        report_content += f"""
## 📝 详细数据

### 原始测试数据
- 测试开始时间: {self.results[0]['timestamp'] if self.results else 'N/A'}
- 测试结束时间: {self.results[-1]['timestamp'] if self.results else 'N/A'}
- 数据样本数: {len(self.results)}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        os.makedirs('tests/reports', exist_ok=True)
        report_path = f"tests/reports/{output_file}"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 性能测试报告已生成: {report_path}")
        return report_path
    
    def save_raw_data(self, filename="performance_raw_data.csv"):
        """保存原始测试数据"""
        os.makedirs('tests/reports', exist_ok=True)
        csv_path = f"tests/reports/{filename}"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'endpoint', 'method', 'response_time', 'status', 'success']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    'timestamp': result.get('timestamp', ''),
                    'endpoint': result.get('endpoint', ''),
                    'method': result.get('method', ''),
                    'response_time': result.get('response_time', 0),
                    'status': result.get('status', 0),
                    'success': result.get('success', False)
                })
        
        print(f"💾 原始数据已保存: {csv_path}")

async def main():
    """主函数"""
    print("🎯 能源交易平台性能测试")
    print("=" * 50)
    
    tester = PerformanceTest()
    
    # 运行性能测试 (60秒，50并发)
    await tester.run_performance_test(test_duration=60, concurrent_requests=50)
    
    # 分析结果
    analysis = tester.analyze_results()
    
    if analysis:
        # 生成报告
        tester.generate_report(analysis)
        tester.save_raw_data()
        
        # 打印关键指标
        print("\n📊 关键性能指标:")
        print(f"   平均响应时间: {analysis['average_response_time']:.3f}s")
        print(f"   成功率: {analysis['success_rate']:.2f}%")
        print(f"   总请求数: {analysis['total_requests']}")
        
        # 检查是否达到目标
        if analysis['average_response_time'] < 3:
            print("   ✅ 性能目标达成！")
        else:
            print("   ❌ 性能目标未达成")

if __name__ == "__main__":
    asyncio.run(main()) 