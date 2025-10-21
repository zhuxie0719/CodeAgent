#!/usr/bin/env python3
"""
从GitHub获取真实的Pull Request修复数据
生成评判系统所需的参考数据库
"""

import requests
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import time


class GitHubPRFetcher:
    """从GitHub获取PR数据的工具类"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        初始化GitHub API客户端
        
        Args:
            github_token: GitHub Personal Access Token（可选，但推荐使用以避免速率限制）
        """
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CodeAgent-PRFetcher/1.0'
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
        
        self.base_url = "https://api.github.com"
    
    def fetch_issue_data(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """获取Issue详细信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取Issue数据失败: {e}")
            return {}
    
    def fetch_pr_data(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """获取PR详细信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取PR数据失败: {e}")
            return {}
    
    def fetch_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """获取PR修改的文件列表"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取PR文件列表失败: {e}")
            return []
    
    def fetch_pr_commits(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """获取PR的提交列表"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取PR提交列表失败: {e}")
            return []
    
    def find_related_pr(self, owner: str, repo: str, issue_number: int) -> Optional[int]:
        """查找关联的PR编号"""
        # 方法1: 从Issue的events中查找
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/events"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            events = response.json()
            
            for event in events:
                if event.get('event') == 'referenced':
                    # 查找提到这个issue的PR
                    commit_url = event.get('commit_url')
                    if commit_url:
                        # 通过commit查找PR
                        pass
            
            # 方法2: 搜索提到这个issue的PR
            search_url = f"{self.base_url}/search/issues"
            params = {
                'q': f'repo:{owner}/{repo} is:pr {issue_number} in:body',
                'sort': 'created',
                'order': 'asc'
            }
            
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            results = response.json()
            
            if results.get('items'):
                # 返回第一个相关PR
                pr_url = results['items'][0].get('pull_request', {}).get('url')
                if pr_url:
                    pr_number = int(pr_url.split('/')[-1])
                    return pr_number
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 查找关联PR失败: {e}")
        
        return None
    
    def extract_fix_data(self, owner: str, repo: str, issue_number: int, pr_number: Optional[int] = None) -> Dict[str, Any]:
        """
        提取完整的修复数据
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: Issue编号
            pr_number: PR编号（可选，如果不提供会自动查找）
        
        Returns:
            包含完整修复信息的字典
        """
        print(f"\n{'='*80}")
        print(f"提取Issue #{issue_number}的修复数据")
        print(f"{'='*80}\n")
        
        # 获取Issue信息
        print("📥 获取Issue信息...")
        issue_data = self.fetch_issue_data(owner, repo, issue_number)
        
        if not issue_data:
            return {}
        
        print(f"✅ Issue标题: {issue_data.get('title', 'Unknown')}")
        
        # 查找关联的PR
        if not pr_number:
            print("🔍 查找关联的PR...")
            pr_number = self.find_related_pr(owner, repo, issue_number)
            
            if not pr_number:
                print("⚠️ 未找到关联的PR，尝试使用Issue编号作为PR编号")
                pr_number = issue_number
        
        print(f"📌 PR编号: #{pr_number}")
        
        # 获取PR信息
        print("📥 获取PR信息...")
        pr_data = self.fetch_pr_data(owner, repo, pr_number)
        
        if not pr_data:
            print("❌ 无法获取PR数据")
            return {}
        
        print(f"✅ PR标题: {pr_data.get('title', 'Unknown')}")
        
        # 获取修改的文件
        print("📥 获取修改的文件列表...")
        files = self.fetch_pr_files(owner, repo, pr_number)
        print(f"✅ 共修改 {len(files)} 个文件")
        
        # 获取提交信息
        print("📥 获取提交信息...")
        commits = self.fetch_pr_commits(owner, repo, pr_number)
        print(f"✅ 共 {len(commits)} 个提交")
        
        # 提取文件变更信息
        files_changed = []
        test_files = []
        code_changes = []
        
        for file in files:
            filename = file.get('filename', '')
            files_changed.append(filename)
            
            if 'test' in filename.lower():
                test_files.append(filename)
            
            # 提取代码变更详情
            code_changes.append({
                'filename': filename,
                'status': file.get('status', 'modified'),
                'additions': file.get('additions', 0),
                'deletions': file.get('deletions', 0),
                'changes': file.get('changes', 0),
                'patch': file.get('patch', '')  # diff内容
            })
        
        # 提取修复策略（从PR描述和提交信息）
        fix_strategy = self._extract_fix_strategy(pr_data, commits)
        
        # 构建完整的修复数据
        fix_data = {
            'issue_id': f'{repo}#{issue_number}',
            'issue_number': str(issue_number),
            'pr_number': str(pr_number),
            'title': issue_data.get('title', ''),
            'description': issue_data.get('body', ''),
            'pr_title': pr_data.get('title', ''),
            'pr_description': pr_data.get('body', ''),
            'github_fix': {
                'files_changed': files_changed,
                'primary_file': files_changed[0] if files_changed else '',
                'lines_added': pr_data.get('additions', 0),
                'lines_removed': pr_data.get('deletions', 0),
                'fix_strategy': fix_strategy,
                'code_changes_summary': self._summarize_changes(code_changes),
                'test_files': test_files,
                'commits': [
                    {
                        'sha': commit.get('sha', ''),
                        'message': commit.get('commit', {}).get('message', '')
                    }
                    for commit in commits
                ],
                'detailed_changes': code_changes  # 包含完整的diff
            },
            'url': f"https://github.com/{owner}/{repo}/issues/{issue_number}",
            'pr_url': f"https://github.com/{owner}/{repo}/pull/{pr_number}"
        }
        
        print("\n✅ 修复数据提取完成！")
        return fix_data
    
    def _extract_fix_strategy(self, pr_data: Dict, commits: List[Dict]) -> str:
        """从PR和提交信息中提取修复策略"""
        strategies = []
        
        # 从PR描述中提取
        pr_body = pr_data.get('body', '')
        if pr_body:
            # 简单处理：取前200字符作为策略描述
            strategies.append(pr_body[:200])
        
        # 从提交信息中提取
        for commit in commits:
            message = commit.get('commit', {}).get('message', '')
            if message:
                # 取提交信息的第一行
                first_line = message.split('\n')[0]
                if first_line and first_line not in strategies:
                    strategies.append(first_line)
        
        return ' | '.join(strategies) if strategies else '修复策略未明确说明'
    
    def _summarize_changes(self, code_changes: List[Dict]) -> List[str]:
        """总结代码变更"""
        summary = []
        
        for change in code_changes:
            filename = change['filename']
            status = change['status']
            additions = change['additions']
            deletions = change['deletions']
            
            if status == 'added':
                summary.append(f"新增文件 {filename}")
            elif status == 'removed':
                summary.append(f"删除文件 {filename}")
            elif status == 'modified':
                summary.append(f"修改 {filename}: +{additions}/-{deletions}")
            elif status == 'renamed':
                summary.append(f"重命名文件 {filename}")
        
        return summary


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='从GitHub获取PR修复数据')
    parser.add_argument('--owner', type=str, default='pallets', help='仓库所有者')
    parser.add_argument('--repo', type=str, default='flask', help='仓库名称')
    parser.add_argument('--issues', type=str, required=True, help='Issue编号，逗号分隔（如: 4041,4019,4053）')
    parser.add_argument('--token', type=str, help='GitHub Personal Access Token（推荐）')
    parser.add_argument('--output', type=str, default='github_pr_data.json', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 创建fetcher
    fetcher = GitHubPRFetcher(args.token)
    
    # 解析issue列表
    issue_numbers = [int(num.strip()) for num in args.issues.split(',')]
    
    # 提取所有issue的修复数据
    all_fix_data = {}
    
    for issue_num in issue_numbers:
        try:
            fix_data = fetcher.extract_fix_data(args.owner, args.repo, issue_num)
            if fix_data:
                issue_id = fix_data['issue_id']
                all_fix_data[issue_id] = fix_data
                
                # 避免速率限制
                time.sleep(1)
        except Exception as e:
            print(f"❌ 处理Issue #{issue_num}时出错: {e}")
            continue
    
    # 保存到文件
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_fix_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ 成功提取 {len(all_fix_data)} 个Issue的修复数据")
    print(f"📄 数据已保存到: {output_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

