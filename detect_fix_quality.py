#!/usr/bin/env python3
"""
通用修复质量检测脚本
支持多种修复输出格式，包括：
1. CodeAgent修复输出
2. code-repair-agent轨迹输出
3. 标准修复JSON格式
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import difflib
import re


class FixOutputParser:
    """修复输出解析器 - 支持多种格式"""
    
    @staticmethod
    def parse_codeagent_output(output_data: Dict) -> Dict[str, Any]:
        """解析CodeAgent的输出格式"""
        return {
            'files_changed': output_data.get('files_changed', []),
            'fix_strategy': output_data.get('fix_strategy', ''),
            'test_files': output_data.get('test_files', []),
            'code_changes': output_data.get('code_changes_summary', []),
            'security_considerations': output_data.get('security_considerations', []),
            'migration_considerations': output_data.get('migration_considerations', []),
            'runtime_tests': output_data.get('runtime_tests', []),
            'tests_passed': output_data.get('functional_tests_passed', False)
        }
    
    @staticmethod
    def parse_code_repair_agent_output(trajectory_data: Dict) -> Dict[str, Any]:
        """
        解析code-repair-agent的轨迹输出
        
        轨迹格式示例:
        {
            "trajectory": [
                {
                    "action": "bash command or edit",
                    "thought": "agent's reasoning",
                    "observation": "command output"
                }
            ],
            "info": {
                "exit_status": "success/fail",
                ...
            }
        }
        """
        trajectory = trajectory_data.get('trajectory', [])
        
        # 从轨迹中提取文件变更
        files_changed = []
        code_changes = []
        test_files = []
        fix_strategy_parts = []
        
        for step in trajectory:
            action = step.get('action', '')
            thought = step.get('thought', '')
            observation = step.get('observation', '')
            
            # 提取修改的文件
            # 匹配编辑操作: edit <file>, vim <file>, sed -i <file> 等
            edit_patterns = [
                r'edit\s+([^\s]+)',
                r'vim\s+([^\s]+)',
                r'nano\s+([^\s]+)',
                r'sed\s+-i.*?\s+([^\s]+)',
                r'cat\s+>\s+([^\s]+)',
                r'echo.*?>\s+([^\s]+)'
            ]
            
            for pattern in edit_patterns:
                match = re.search(pattern, action)
                if match:
                    file_path = match.group(1)
                    if file_path not in files_changed:
                        files_changed.append(file_path)
                        
                        # 判断是否为测试文件
                        if 'test' in file_path.lower():
                            test_files.append(file_path)
                        
                        # 提取代码变更详情
                        code_changes.append({
                            'file': file_path,
                            'action': action,
                            'context': thought
                        })
            
            # 提取修复策略（从agent的思考）
            if thought and any(keyword in thought.lower() for keyword in ['fix', 'repair', 'solution', 'change']):
                fix_strategy_parts.append(thought)
        
        # 检查测试是否通过
        info = trajectory_data.get('info', {})
        tests_passed = info.get('exit_status') == 'success'
        
        return {
            'files_changed': files_changed,
            'fix_strategy': ' | '.join(fix_strategy_parts) if fix_strategy_parts else '未提取到修复策略',
            'test_files': test_files,
            'code_changes': code_changes,
            'security_considerations': [],  # code-repair-agent通常不明确标注
            'migration_considerations': [],
            'runtime_tests': [],
            'tests_passed': tests_passed,
            'trajectory': trajectory  # 保留完整轨迹供详细分析
        }
    
    @staticmethod
    def parse_standard_format(data: Dict) -> Dict[str, Any]:
        """解析标准JSON格式"""
        return {
            'files_changed': data.get('files_changed', []),
            'fix_strategy': data.get('fix_strategy', ''),
            'test_files': data.get('test_files', []),
            'code_changes': data.get('code_changes_summary', []),
            'security_considerations': data.get('security_considerations', []),
            'migration_considerations': data.get('migration_considerations', []),
            'runtime_tests': data.get('runtime_tests', []),
            'tests_passed': data.get('functional_tests_passed', False)
        }
    
    @classmethod
    def auto_parse(cls, data: Dict) -> Dict[str, Any]:
        """自动识别格式并解析"""
        # 检测code-repair-agent格式（包含trajectory）
        if 'trajectory' in data:
            print("🔍 检测到code-repair-agent轨迹格式")
            return cls.parse_code_repair_agent_output(data)
        
        # 检测CodeAgent格式（包含fix_strategy和files_changed）
        elif 'fix_strategy' in data and 'files_changed' in data:
            print("🔍 检测到CodeAgent标准格式")
            return cls.parse_codeagent_output(data)
        
        # 尝试标准格式
        else:
            print("🔍 尝试标准格式解析")
            return cls.parse_standard_format(data)


class FixQualityDetector:
    """修复质量检测器"""
    
    def __init__(self, reference_data_file: str):
        """
        初始化检测器
        
        Args:
            reference_data_file: GitHub参考数据文件路径
        """
        self.reference_data = self._load_reference_data(reference_data_file)
    
    def _load_reference_data(self, file_path: str) -> Dict:
        """加载GitHub参考数据"""
        path = Path(file_path)
        if not path.exists():
            print(f"❌ 参考数据文件不存在: {file_path}")
            sys.exit(1)
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def detect(self, fix_output_file: str, issue_id: str) -> Dict[str, Any]:
        """
        检测修复质量
        
        Args:
            fix_output_file: 修复输出文件路径
            issue_id: Issue ID（如: flask#4041）
        
        Returns:
            检测结果字典
        """
        print(f"\n{'='*80}")
        print(f"🔍 开始检测修复质量")
        print(f"{'='*80}\n")
        
        # 加载修复输出
        with open(fix_output_file, 'r', encoding='utf-8') as f:
            fix_output_raw = json.load(f)
        
        # 自动解析格式
        fix_output = FixOutputParser.auto_parse(fix_output_raw)
        
        # 获取参考数据
        reference = self.reference_data.get(issue_id)
        if not reference:
            print(f"❌ 未找到Issue {issue_id}的参考数据")
            return {
                'success': False,
                'error': f'未找到Issue {issue_id}的参考数据'
            }
        
        github_fix = reference.get('github_fix', {})
        
        print(f"📌 Issue: {reference.get('title', 'Unknown')}")
        print(f"🔗 GitHub: {reference.get('url', 'Unknown')}\n")
        
        # 执行多维度检测
        result = {
            'issue_id': issue_id,
            'title': reference.get('title', ''),
            'detection_time': Path(fix_output_file).stat().st_mtime,
            'scores': {},
            'details': {}
        }
        
        # 1. 文件匹配度检测
        file_score = self._detect_file_match(fix_output, github_fix)
        result['scores']['file_match'] = file_score
        
        # 2. 修复策略相似度检测
        strategy_score = self._detect_strategy_similarity(fix_output, github_fix)
        result['scores']['strategy_similarity'] = strategy_score
        
        # 3. 代码变更分析
        changes_score = self._detect_code_changes(fix_output, github_fix)
        result['scores']['code_changes'] = changes_score
        
        # 4. 测试覆盖度检测
        test_score = self._detect_test_coverage(fix_output, github_fix)
        result['scores']['test_coverage'] = test_score
        
        # 5. 测试通过检测
        result['tests_passed'] = fix_output.get('tests_passed', False)
        
        # 计算总分
        weights = {
            'file_match': 0.3,
            'strategy_similarity': 0.3,
            'code_changes': 0.2,
            'test_coverage': 0.2
        }
        
        total_score = sum(result['scores'][k] * w for k, w in weights.items())
        result['total_score'] = total_score
        result['success'] = total_score >= 0.7  # 70%阈值
        
        # 生成详细报告
        self._print_detection_report(result)
        
        return result
    
    def _detect_file_match(self, fix_output: Dict, github_fix: Dict) -> float:
        """检测文件匹配度"""
        print("📁 检测文件匹配度...")
        
        our_files = set(fix_output.get('files_changed', []))
        github_files = set(github_fix.get('files_changed', []))
        
        if not github_files:
            print("  ⚠️ GitHub参考数据中无文件信息")
            return 0.5
        
        # 计算交集和并集
        intersection = our_files & github_files
        union = our_files | github_files
        
        score = len(intersection) / len(union) if union else 0.0
        
        print(f"  - 我们修改的文件: {len(our_files)} 个")
        print(f"  - GitHub修改的文件: {len(github_files)} 个")
        print(f"  - 匹配的文件: {len(intersection)} 个")
        print(f"  - 文件匹配度: {score:.2%}\n")
        
        if intersection:
            print(f"  ✅ 匹配文件: {list(intersection)}")
        if our_files - github_files:
            print(f"  ⚠️ 额外文件: {list(our_files - github_files)}")
        if github_files - our_files:
            print(f"  ❌ 遗漏文件: {list(github_files - our_files)}")
        print()
        
        return score
    
    def _detect_strategy_similarity(self, fix_output: Dict, github_fix: Dict) -> float:
        """检测修复策略相似度"""
        print("🎯 检测修复策略相似度...")
        
        our_strategy = fix_output.get('fix_strategy', '').lower()
        github_strategy = github_fix.get('fix_strategy', '').lower()
        
        if not our_strategy or not github_strategy:
            print("  ⚠️ 修复策略信息不完整")
            return 0.5
        
        # 使用difflib计算文本相似度
        similarity = difflib.SequenceMatcher(None, our_strategy, github_strategy).ratio()
        
        # 关键词匹配
        keywords = self._extract_keywords(github_strategy)
        keyword_matches = sum(1 for kw in keywords if kw in our_strategy)
        keyword_score = keyword_matches / len(keywords) if keywords else 0.5
        
        # 综合评分
        score = similarity * 0.6 + keyword_score * 0.4
        
        print(f"  - 文本相似度: {similarity:.2%}")
        print(f"  - 关键词匹配: {keyword_score:.2%} ({keyword_matches}/{len(keywords)})")
        print(f"  - 策略相似度总分: {score:.2%}\n")
        
        return score
    
    def _detect_code_changes(self, fix_output: Dict, github_fix: Dict) -> float:
        """检测代码变更质量"""
        print("💻 检测代码变更...")
        
        our_changes = fix_output.get('code_changes', [])
        github_changes = github_fix.get('code_changes_summary', [])
        
        if not github_changes:
            print("  ⚠️ GitHub参考数据中无代码变更信息")
            return 0.5
        
        # 比较变更数量
        change_count_score = min(len(our_changes) / len(github_changes), 1.0) if github_changes else 0.5
        
        # 比较变更类型（添加/删除/修改）
        our_lines_added = sum(c.get('additions', 0) for c in our_changes if isinstance(c, dict))
        our_lines_deleted = sum(c.get('deletions', 0) for c in our_changes if isinstance(c, dict))
        
        github_lines_added = github_fix.get('lines_added', 0)
        github_lines_deleted = github_fix.get('lines_removed', 0)
        
        # 计算变更规模相似度
        if github_lines_added > 0:
            add_similarity = min(our_lines_added / github_lines_added, 2.0) / 2.0
        else:
            add_similarity = 1.0 if our_lines_added == 0 else 0.5
        
        if github_lines_deleted > 0:
            del_similarity = min(our_lines_deleted / github_lines_deleted, 2.0) / 2.0
        else:
            del_similarity = 1.0 if our_lines_deleted == 0 else 0.5
        
        score = (change_count_score + add_similarity + del_similarity) / 3
        
        print(f"  - 变更数量: 我们 {len(our_changes)}, GitHub {len(github_changes)}")
        print(f"  - 添加行数: 我们 {our_lines_added}, GitHub {github_lines_added}")
        print(f"  - 删除行数: 我们 {our_lines_deleted}, GitHub {github_lines_deleted}")
        print(f"  - 代码变更得分: {score:.2%}\n")
        
        return score
    
    def _detect_test_coverage(self, fix_output: Dict, github_fix: Dict) -> float:
        """检测测试覆盖度"""
        print("🧪 检测测试覆盖度...")
        
        our_tests = set(fix_output.get('test_files', []))
        github_tests = set(github_fix.get('test_files', []))
        
        if not github_tests:
            # 如果GitHub没有测试文件，我们也没有，算通过
            score = 1.0 if not our_tests else 0.7
            print(f"  - GitHub未添加测试文件")
            print(f"  - 测试覆盖度得分: {score:.2%}\n")
            return score
        
        # 计算测试文件匹配度
        intersection = our_tests & github_tests
        score = len(intersection) / len(github_tests)
        
        print(f"  - 我们的测试文件: {len(our_tests)} 个")
        print(f"  - GitHub的测试文件: {len(github_tests)} 个")
        print(f"  - 匹配的测试文件: {len(intersection)} 个")
        print(f"  - 测试覆盖度得分: {score:.2%}\n")
        
        if intersection:
            print(f"  ✅ 匹配测试: {list(intersection)}")
        if our_tests - github_tests:
            print(f"  ➕ 额外测试: {list(our_tests - github_tests)}")
        if github_tests - our_tests:
            print(f"  ❌ 遗漏测试: {list(github_tests - our_tests)}")
        print()
        
        return score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取：取长度>3的单词
        words = re.findall(r'\b\w{4,}\b', text.lower())
        # 去除常见词
        stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'been', 'were'}
        return [w for w in words if w not in stop_words]
    
    def _print_detection_report(self, result: Dict):
        """打印检测报告"""
        print(f"\n{'='*80}")
        print(f"📊 检测结果汇总")
        print(f"{'='*80}\n")
        
        print(f"Issue: {result['title']}")
        print(f"Issue ID: {result['issue_id']}\n")
        
        print("各维度得分:")
        for key, score in result['scores'].items():
            print(f"  - {key:25s}: {score:6.2%}")
        
        print(f"\n总分: {result['total_score']:.2%}")
        print(f"测试通过: {'✅ 是' if result.get('tests_passed') else '❌ 否'}")
        
        if result['success']:
            print(f"\n✅ 修复质量达标！")
        else:
            print(f"\n❌ 修复质量未达标")
            gap = 0.7 - result['total_score']
            print(f"   距离阈值(70%)还差: {gap:.2%}")
        
        print(f"\n{'='*80}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检测修复质量')
    parser.add_argument('--fix-output', type=str, required=True, help='修复输出文件路径')
    parser.add_argument('--issue', type=str, required=True, help='Issue ID（如: flask#4041）')
    parser.add_argument('--reference', type=str, default='github_pr_data.json', help='GitHub参考数据文件')
    parser.add_argument('--output', type=str, default='detection_result.json', help='检测结果输出文件')
    
    args = parser.parse_args()
    
    # 创建检测器
    detector = FixQualityDetector(args.reference)
    
    # 执行检测
    result = detector.detect(args.fix_output, args.issue)
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📄 检测结果已保存到: {args.output}")


if __name__ == "__main__":
    main()

