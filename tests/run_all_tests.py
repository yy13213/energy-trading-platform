#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源交易平台完整测试套件
批量运行所有测试并生成综合报告
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# 添加性能测试模块到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'performance'))

from performance.performance_test import PerformanceTest
from performance.concurrent_test import ConcurrentTest

class TestSuite:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.test_results = {}
        
    async def run_all_tests(self):
        """运行所有测试"""
        print("🎯 能源交易平台完整测试套件")
        print("=" * 60)
        print(f"📅 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 测试目标: {self.base_url}")
        print()
        
        # 1. 运行性能测试
        print("🚀 第一阶段：性能测试")
        print("-" * 40)
        performance_result = await self.run_performance_test()
        
        print("\n" + "="*60 + "\n")
        
        # 2. 运行并发测试  
        print("🚀 第二阶段：并发测试")
        print("-" * 40)
        concurrent_result = await self.run_concurrent_test()
        
        print("\n" + "="*60 + "\n")
        
        # 3. 生成综合报告
        print("📊 第三阶段：生成综合报告")
        print("-" * 40)
        self.generate_comprehensive_report(performance_result, concurrent_result)
        
        print("\n🎉 所有测试完成！")
        
    async def run_performance_test(self):
        """运行性能测试"""
        try:
            tester = PerformanceTest(self.base_url)
            
            # 运行性能测试 (60秒，50并发)
            await tester.run_performance_test(test_duration=60, concurrent_requests=50)
            
            # 分析结果
            analysis = tester.analyze_results()
            
            if analysis:
                # 生成报告
                tester.generate_report(analysis, "performance_report.md")
                tester.save_raw_data("performance_raw_data.csv")
                
                print(f"✅ 性能测试完成")
                print(f"   📊 平均响应时间: {analysis['average_response_time']:.3f}s")
                print(f"   📊 成功率: {analysis['success_rate']:.2f}%")
                print(f"   📊 总请求数: {analysis['total_requests']}")
                
                return {
                    'success': True,
                    'analysis': analysis,
                    'target_met': analysis['average_response_time'] < 3
                }
            else:
                print("❌ 性能测试失败")
                return {'success': False, 'analysis': None, 'target_met': False}
                
        except Exception as e:
            print(f"❌ 性能测试异常: {e}")
            return {'success': False, 'analysis': None, 'target_met': False, 'error': str(e)}
    
    async def run_concurrent_test(self):
        """运行并发测试"""
        try:
            tester = ConcurrentTest(self.base_url)
            
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
                tester.generate_concurrent_report(analysis, "concurrent_report.md")
                tester.save_concurrent_raw_data("concurrent_raw_data.csv")
                
                print(f"✅ 并发测试完成")
                print(f"   📊 峰值并发用户数: {analysis['max_concurrent_users']}")
                print(f"   📊 平均并发用户数: {analysis['avg_concurrent_users']:.1f}")
                print(f"   📊 成功率: {analysis['success_rate']:.2f}%")
                print(f"   📊 平均响应时间: {analysis['average_response_time']:.3f}s")
                
                return {
                    'success': True,
                    'analysis': analysis,
                    'target_met': analysis['max_concurrent_users'] > 200
                }
            else:
                print("❌ 并发测试失败")
                return {'success': False, 'analysis': None, 'target_met': False}
                
        except Exception as e:
            print(f"❌ 并发测试异常: {e}")
            return {'success': False, 'analysis': None, 'target_met': False, 'error': str(e)}
    
    def generate_comprehensive_report(self, performance_result, concurrent_result):
        """生成综合测试报告"""
        report_content = f"""# 🚀 能源交易平台综合测试报告

## 📊 测试总览

- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试目标系统**: {self.base_url}
- **测试类型**: 性能测试 + 并发测试

## 🎯 测试目标与结果

### 性能测试目标
- **目标**: 平均响应时间 < 3秒
- **结果**: {'✅ 达成' if performance_result.get('target_met', False) else '❌ 未达成'}

### 并发测试目标  
- **目标**: 并发用户数 > 200
- **结果**: {'✅ 达成' if concurrent_result.get('target_met', False) else '❌ 未达成'}

## 📈 详细测试结果

### 1. 性能测试结果

"""
        
        if performance_result.get('success', False) and performance_result.get('analysis'):
            perf_analysis = performance_result['analysis']
            report_content += f"""
| 指标 | 数值 | 状态 |
|------|------|------|
| 平均响应时间 | {perf_analysis['average_response_time']:.3f}s | {'✅ 优秀' if perf_analysis['average_response_time'] < 1 else ('✅ 良好' if perf_analysis['average_response_time'] < 3 else '❌ 需要优化')} |
| 成功率 | {perf_analysis['success_rate']:.2f}% | {'✅ 优秀' if perf_analysis['success_rate'] > 99 else ('✅ 良好' if perf_analysis['success_rate'] > 95 else '❌ 需要改进')} |
| 总请求数 | {perf_analysis['total_requests']} | - |
| P95响应时间 | {perf_analysis['p95_response_time']:.3f}s | {'✅ 良好' if perf_analysis['p95_response_time'] < 5 else '⚠️ 需要关注'} |
| P99响应时间 | {perf_analysis['p99_response_time']:.3f}s | {'✅ 良好' if perf_analysis['p99_response_time'] < 8 else '⚠️ 需要关注'} |
"""
        else:
            report_content += "❌ 性能测试失败或无有效数据\n"
            if 'error' in performance_result:
                report_content += f"错误信息: {performance_result['error']}\n"
        
        report_content += "\n### 2. 并发测试结果\n"
        
        if concurrent_result.get('success', False) and concurrent_result.get('analysis'):
            conc_analysis = concurrent_result['analysis']
            report_content += f"""
| 指标 | 数值 | 状态 |
|------|------|------|
| 峰值并发用户数 | {conc_analysis['max_concurrent_users']} | {'✅ 优秀' if conc_analysis['max_concurrent_users'] > 300 else ('✅ 良好' if conc_analysis['max_concurrent_users'] > 200 else '❌ 未达标')} |
| 平均并发用户数 | {conc_analysis['avg_concurrent_users']:.1f} | - |
| 并发成功率 | {conc_analysis['success_rate']:.2f}% | {'✅ 优秀' if conc_analysis['success_rate'] > 99 else ('✅ 良好' if conc_analysis['success_rate'] > 95 else '❌ 需要改进')} |
| 并发平均响应时间 | {conc_analysis['average_response_time']:.3f}s | {'✅ 优秀' if conc_analysis['average_response_time'] < 3 else ('✅ 良好' if conc_analysis['average_response_time'] < 5 else '⚠️ 需要优化')} |
| 总请求数 | {conc_analysis['total_requests']} | - |
"""
        else:
            report_content += "❌ 并发测试失败或无有效数据\n"
            if 'error' in concurrent_result:
                report_content += f"错误信息: {concurrent_result['error']}\n"
        
        # 综合评估
        performance_pass = performance_result.get('target_met', False)
        concurrent_pass = concurrent_result.get('target_met', False)
        
        report_content += f"""
## 🎯 综合评估

### 测试目标达成情况
- **性能测试**: {'✅ 通过' if performance_pass else '❌ 未通过'}
- **并发测试**: {'✅ 通过' if concurrent_pass else '❌ 未通过'}

### 整体评级
"""
        
        if performance_pass and concurrent_pass:
            report_content += "**🏆 优秀** - 系统性能完全满足要求\n"
        elif performance_pass or concurrent_pass:
            report_content += "**⚠️ 良好** - 部分测试通过，需要针对性优化\n"
        else:
            report_content += "**❌ 需要改进** - 系统性能不满足要求，需要全面优化\n"
        
        report_content += f"""
### 优化建议

"""
        
        # 根据测试结果给出具体建议
        if not performance_pass:
            report_content += "#### 性能优化建议\n"
            report_content += "- 🔧 优化数据库查询，添加适当的索引\n"
            report_content += "- 🔧 增强缓存策略，减少重复计算\n"
            report_content += "- 🔧 考虑使用异步处理和队列系统\n"
            report_content += "- 🔧 优化API响应数据结构，减少传输量\n\n"
        
        if not concurrent_pass:
            report_content += "#### 并发优化建议\n"
            report_content += "- 🔧 增加服务器连接池大小\n"
            report_content += "- 🔧 优化数据库连接池配置\n"
            report_content += "- 🔧 考虑使用负载均衡和集群部署\n"
            report_content += "- 🔧 添加限流和熔断机制\n\n"
        
        if performance_pass and concurrent_pass:
            report_content += "#### 持续优化建议\n"
            report_content += "- ✨ 系统性能表现优秀，建议定期进行性能监控\n"
            report_content += "- ✨ 可以考虑进一步提升并发处理能力\n"
            report_content += "- ✨ 建立性能基线，持续跟踪性能变化\n\n"
        
        report_content += f"""
## 📝 测试环境信息

- **测试工具**: Python异步性能测试框架
- **测试方法**: 
  - 性能测试: 60秒持续压测，50并发请求
  - 并发测试: 250用户目标，30秒爬坡，120秒持续测试
- **测试端点**: 7个主要业务API端点
- **测试数据**: 详见各项测试的原始数据文件

## 📄 相关文件

- `performance_report.md` - 详细性能测试报告
- `concurrent_report.md` - 详细并发测试报告  
- `performance_raw_data.csv` - 性能测试原始数据
- `concurrent_raw_data.csv` - 并发测试原始数据

---
*综合报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存综合报告
        os.makedirs('tests/reports', exist_ok=True)
        report_path = "tests/reports/comprehensive_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 综合测试报告已生成: {report_path}")
        
        # 打印测试总结
        print("\n📊 测试总结:")
        print(f"   性能测试: {'✅ 通过' if performance_pass else '❌ 未通过'}")
        print(f"   并发测试: {'✅ 通过' if concurrent_pass else '❌ 未通过'}")
        
        if performance_pass and concurrent_pass:
            print("   🏆 整体评级: 优秀")
        elif performance_pass or concurrent_pass:
            print("   ⚠️ 整体评级: 良好")
        else:
            print("   ❌ 整体评级: 需要改进")

async def main():
    """主函数"""
    # 检查命令行参数
    base_url = "http://127.0.0.1:8080"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    # 运行测试套件
    suite = TestSuite(base_url)
    await suite.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试套件执行失败: {e}")
        sys.exit(1) 