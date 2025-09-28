"""
决策引擎实现
负责分析缺陷复杂度、选择修复策略、评估风险
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

from .message_types import DEFECT_TYPES, FIX_STRATEGIES


class DecisionEngine:
    """决策引擎 - 系统的智能决策核心"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # AI模型配置
        self.ai_model = config.get("ai_model", "deepseek")
        self.confidence_threshold = config.get("confidence_threshold", 0.8)
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        
        # 决策规则
        self.simple_rules = DEFECT_TYPES.get("simple", {})
        self.medium_rules = DEFECT_TYPES.get("medium", {})
        self.complex_rules = DEFECT_TYPES.get("complex", {})
        
        # 修复策略映射
        self.fix_strategies = FIX_STRATEGIES
        
        # 历史决策记录（用于学习优化）
        self.decision_history: List[Dict[str, Any]] = []
        
        # 统计信息
        self.stats = {
            "decisions_made": 0,
            "auto_fix_decisions": 0,
            "ai_assisted_decisions": 0,
            "manual_review_decisions": 0,
            "successful_decisions": 0,
            "failed_decisions": 0
        }
    
    async def start(self):
        """启动决策引擎"""
        self.is_running = True
        self.logger.info("决策引擎启动中...")
        self.logger.info(f"配置: AI模型={self.ai_model}, 置信度阈值={self.confidence_threshold}")
        self.logger.info("决策引擎已启动")
    
    async def stop(self):
        """停止决策引擎"""
        self.is_running = False
        self.logger.info("决策引擎已停止")
    
    async def analyze_complexity(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析缺陷复杂度并制定修复策略"""
        self.logger.info(f"开始分析 {len(issues)} 个缺陷的复杂度")
        
        decisions = {
            "auto_fixable": [],      # 可自动修复
            "ai_assisted": [],       # 需要AI辅助
            "manual_review": [],     # 需要人工审查
            "skip": [],              # 跳过或延迟处理
            "summary": {
                "total_issues": len(issues),
                "auto_fixable_count": 0,
                "ai_assisted_count": 0,
                "manual_review_count": 0,
                "skip_count": 0
            }
        }
        
        for issue in issues:
            try:
                decision = await self._analyze_single_issue(issue)
                
                if decision["category"] == "auto_fixable":
                    decisions["auto_fixable"].append(decision)
                    decisions["summary"]["auto_fixable_count"] += 1
                elif decision["category"] == "ai_assisted":
                    decisions["ai_assisted"].append(decision)
                    decisions["summary"]["ai_assisted_count"] += 1
                elif decision["category"] == "manual_review":
                    decisions["manual_review"].append(decision)
                    decisions["summary"]["manual_review_count"] += 1
                else:
                    decisions["skip"].append(decision)
                    decisions["summary"]["skip_count"] += 1
                    
            except Exception as e:
                self.logger.error(f"分析缺陷失败: {issue.get('type', 'unknown')} - {e}")
                # 将失败的缺陷标记为需要人工审查
                decisions["manual_review"].append({
                    "issue": issue,
                    "category": "manual_review",
                    "strategy": "manual_review",
                    "confidence": 0.0,
                    "reason": f"分析失败: {str(e)}"
                })
        
        self.stats["decisions_made"] += len(issues)
        self.logger.info(f"复杂度分析完成: {decisions['summary']}")
        
        return decisions
    
    async def _analyze_single_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个缺陷的复杂度"""
        issue_type = issue.get("type", "unknown")
        severity = issue.get("severity", "info")
        
        # 1. 基于规则的决策
        rule_decision = self._rule_based_decision(issue_type, severity)
        if rule_decision["confidence"] > self.confidence_threshold:
            return rule_decision
        
        # 2. 基于上下文的增强决策
        context_decision = await self._context_enhanced_decision(issue)
        if context_decision["confidence"] > self.confidence_threshold:
            return context_decision
        
        # 3. AI增强决策
        ai_decision = await self._ai_enhanced_decision(issue)
        
        # 4. 综合决策
        final_decision = self._combine_decisions(rule_decision, context_decision, ai_decision)
        
        # 记录决策历史
        self._record_decision(final_decision, issue)
        
        return final_decision
    
    def _rule_based_decision(self, issue_type: str, severity: str) -> Dict[str, Any]:
        """基于规则的决策"""
        # 检查是否为简单缺陷
        if issue_type in self.simple_rules:
            strategy = self.fix_strategies.get(issue_type, "auto_fix")
            return {
                "category": "auto_fixable",
                "strategy": strategy,
                "confidence": 0.9,
                "reason": "基于规则判断为简单缺陷",
                "rule_source": "simple_rules"
            }
        
        # 检查是否为中等缺陷
        if issue_type in self.medium_rules:
            strategy = self.fix_strategies.get(issue_type, "ai_assisted")
            return {
                "category": "ai_assisted", 
                "strategy": strategy,
                "confidence": 0.7,
                "reason": "基于规则判断为中等缺陷",
                "rule_source": "medium_rules"
            }
        
        # 检查是否为复杂缺陷
        if issue_type in self.complex_rules:
            strategy = self.fix_strategies.get(issue_type, "manual_review")
            return {
                "category": "manual_review",
                "strategy": strategy, 
                "confidence": 0.8,
                "reason": "基于规则判断为复杂缺陷",
                "rule_source": "complex_rules"
            }
        
        # 基于严重性的决策
        if severity == "error":
            return {
                "category": "manual_review",
                "strategy": "manual_review",
                "confidence": 0.6,
                "reason": "错误级别缺陷需要人工审查",
                "rule_source": "severity_based"
            }
        elif severity == "warning":
            return {
                "category": "ai_assisted",
                "strategy": "ai_analysis_required",
                "confidence": 0.5,
                "reason": "警告级别缺陷需要AI分析",
                "rule_source": "severity_based"
            }
        
        # 默认决策
        return {
            "category": "ai_assisted",
            "strategy": "ai_analysis_required",
            "confidence": 0.3,
            "reason": "未知类型缺陷，需要AI分析",
            "rule_source": "default"
        }
    
    async def _context_enhanced_decision(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """基于上下文的增强决策"""
        # 获取更多上下文信息
        file_path = issue.get("file_path", "")
        line_number = issue.get("line", 0)
        message = issue.get("message", "")
        
        # 基于文件类型的决策
        if file_path.endswith(('.py', '.pyw')):
            # Python文件，可能有更多自动修复选项
            if "import" in message.lower() and "unused" in message.lower():
                return {
                    "category": "auto_fixable",
                    "strategy": "auto_remove",
                    "confidence": 0.8,
                    "reason": "Python未使用导入可以自动删除",
                    "rule_source": "context_enhanced"
                }
        
        # 基于消息内容的决策
        if "format" in message.lower() or "indent" in message.lower():
            return {
                "category": "auto_fixable",
                "strategy": "auto_format",
                "confidence": 0.7,
                "reason": "格式化问题可以自动修复",
                "rule_source": "context_enhanced"
            }
        
        # 基于行号的决策（简单启发式）
        if line_number <= 10:  # 文件开头的错误通常更简单
            return {
                "category": "auto_fixable",
                "strategy": "auto_fix",
                "confidence": 0.4,
                "reason": "文件开头的错误可能较简单",
                "rule_source": "context_enhanced"
            }
        
        return {
            "category": "ai_assisted",
            "strategy": "ai_analysis_required", 
            "confidence": 0.3,
            "reason": "上下文分析无法确定策略",
            "rule_source": "context_enhanced"
        }
    
    async def _ai_enhanced_decision(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """AI增强决策"""
        try:
            # 构建AI分析提示
            prompt = self._build_ai_prompt(issue)
            
            # 调用AI API（这里使用模拟，实际需要调用DeepSeek API）
            ai_result = await self._call_ai_api(prompt)
            
            # 解析AI结果
            decision = self._parse_ai_result(ai_result, issue)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"AI增强决策失败: {e}")
            return {
                "category": "manual_review",
                "strategy": "manual_review",
                "confidence": 0.1,
                "reason": f"AI分析失败: {str(e)}",
                "rule_source": "ai_enhanced_failed"
            }
    
    def _build_ai_prompt(self, issue: Dict[str, Any]) -> str:
        """构建AI分析提示"""
        issue_type = issue.get("type", "unknown")
        message = issue.get("message", "")
        file_path = issue.get("file_path", "")
        line = issue.get("line", 0)
        
        prompt = f"""
请分析以下代码缺陷的复杂度和修复策略：

缺陷类型: {issue_type}
错误信息: {message}
文件路径: {file_path}
行号: {line}

请判断这个缺陷的复杂度：
1. 简单 - 可以直接自动修复（如格式化、删除未使用导入等）
2. 中等 - 需要AI辅助修复（如重命名、重构建议等）
3. 复杂 - 需要人工审查（如安全漏洞、业务逻辑错误等）

请以JSON格式返回分析结果：
{{
    "complexity": "simple|medium|complex",
    "strategy": "auto_fix|ai_assisted|manual_review",
    "confidence": 0.0-1.0,
    "reason": "分析理由",
    "suggestions": ["修复建议1", "修复建议2"]
}}
"""
        return prompt
    
    async def _call_ai_api(self, prompt: str) -> Dict[str, Any]:
        """调用AI API进行分析"""
        # 这里是模拟实现，实际需要调用DeepSeek API
        # 模拟AI返回结果
        await asyncio.sleep(0.1)  # 模拟API调用延迟
        
        # 模拟AI分析结果
        return {
            "complexity": "medium",
            "strategy": "ai_assisted", 
            "confidence": 0.7,
            "reason": "AI分析认为这是一个中等复杂度的缺陷",
            "suggestions": ["建议使用AI辅助修复", "需要进一步分析代码上下文"]
        }
    
    def _parse_ai_result(self, ai_result: Dict[str, Any], issue: Dict[str, Any]) -> Dict[str, Any]:
        """解析AI分析结果"""
        complexity = ai_result.get("complexity", "medium")
        strategy = ai_result.get("strategy", "ai_assisted")
        confidence = ai_result.get("confidence", 0.5)
        reason = ai_result.get("reason", "AI分析结果")
        
        # 映射复杂度到决策类别
        category_map = {
            "simple": "auto_fixable",
            "medium": "ai_assisted", 
            "complex": "manual_review"
        }
        
        category = category_map.get(complexity, "ai_assisted")
        
        return {
            "category": category,
            "strategy": strategy,
            "confidence": confidence,
            "reason": reason,
            "ai_suggestions": ai_result.get("suggestions", []),
            "rule_source": "ai_enhanced"
        }
    
    def _combine_decisions(self, *decisions: Dict[str, Any]) -> Dict[str, Any]:
        """综合多个决策结果"""
        # 选择置信度最高的决策
        best_decision = max(decisions, key=lambda x: x.get("confidence", 0))
        
        # 如果最高置信度仍然很低，则选择最保守的策略
        if best_decision["confidence"] < 0.4:
            best_decision = {
                "category": "manual_review",
                "strategy": "manual_review",
                "confidence": 0.3,
                "reason": "综合决策：置信度较低，选择人工审查",
                "rule_source": "combined"
            }
        
        return best_decision
    
    def _record_decision(self, decision: Dict[str, Any], issue: Dict[str, Any]):
        """记录决策历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "issue_type": issue.get("type", "unknown"),
            "issue_severity": issue.get("severity", "info"),
            "decision": decision,
            "issue_id": issue.get("id", "unknown")
        }
        
        self.decision_history.append(record)
        
        # 限制历史记录数量
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-500:]
    
    async def select_fix_strategy(self, issue: Dict[str, Any]) -> str:
        """选择修复策略"""
        decision = await self._analyze_single_issue(issue)
        strategy = decision.get("strategy", "manual_review")
        
        self.logger.info(f"为缺陷 {issue.get('type', 'unknown')} 选择策略: {strategy}")
        return strategy
    
    async def evaluate_risk(self, fix_plan: Dict[str, Any]) -> float:
        """评估修复风险"""
        risk_factors = []
        
        # 基于修复类型的风险
        fix_type = fix_plan.get("type", "unknown")
        if fix_type in ["auto_remove", "auto_format"]:
            risk_factors.append(0.1)  # 低风险
        elif fix_type in ["ai_assisted", "ai_refactor"]:
            risk_factors.append(0.3)  # 中等风险
        else:
            risk_factors.append(0.5)  # 高风险
        
        # 基于文件重要性的风险
        file_path = fix_plan.get("file_path", "")
        if "test" in file_path.lower():
            risk_factors.append(0.1)  # 测试文件风险较低
        elif "main" in file_path.lower() or "core" in file_path.lower():
            risk_factors.append(0.4)  # 核心文件风险较高
        
        # 基于修改范围的风险
        changes_count = fix_plan.get("changes_count", 1)
        if changes_count > 10:
            risk_factors.append(0.3)
        elif changes_count > 5:
            risk_factors.append(0.2)
        else:
            risk_factors.append(0.1)
        
        # 计算综合风险分数
        risk_score = sum(risk_factors) / len(risk_factors)
        
        self.logger.info(f"修复风险评估: {risk_score:.2f}")
        return min(risk_score, 1.0)  # 确保不超过1.0
    
    async def should_require_human_review(self, issue: Dict[str, Any], risk_score: float) -> bool:
        """判断是否需要人工审查"""
        # 高风险修复需要人工审查
        if risk_score > 0.5:
            return True
        
        # 安全相关缺陷需要人工审查
        security_issues = ["hardcoded_secrets", "unsafe_eval", "unsafe_file_operations", 
                          "missing_input_validation", "insecure_random"]
        if issue.get("type") in security_issues:
            return True
        
        # 错误级别缺陷需要人工审查
        if issue.get("severity") == "error":
            return True
        
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "decision_history_count": len(self.decision_history),
            "config": {
                "ai_model": self.ai_model,
                "confidence_threshold": self.confidence_threshold,
                "max_retry_attempts": self.max_retry_attempts
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "is_running": self.is_running,
            "stats": self.stats,
            "rules_loaded": {
                "simple_rules": len(self.simple_rules),
                "medium_rules": len(self.medium_rules), 
                "complex_rules": len(self.complex_rules)
            }
        }
