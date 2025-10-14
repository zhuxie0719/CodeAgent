#!/usr/bin/env python3
"""
Flask 2.0.0 Issue对比脚本
对比系统检测结果与内置的 25 条金标 Issue（2.0.0→2.0.1/2.0.2/2.0.3 修复）
"""

import json
from pathlib import Path
import sys


def normalize_issue_id(value: str) -> str:
    if not value:
        return ""
    v = str(value).strip()
    if v.startswith("https://github.com/pallets/flask/issues/"):
        try:
            num = v.rsplit("/", 1)[1]
            if num.isdigit():
                return f"flask#{num}"
        except Exception:
            return ""
    if v.startswith("flask#"):
        return v
    if v.startswith("#") and v[1:].isdigit():
        return f"flask#{v[1:]}"
    if v.isdigit():
        return f"flask#{v}"
    return ""


def embedded_gold():
    """内置 25 条 Issue（id、capability、difficulty、first fixed 版本、url）。"""
    def row(n, diff, cap, ver):
        return (
            f"flask#{n}",
            {
                "difficulty": diff,  # simple/medium/hard
                "capability": cap,   # S/A/D
                "fixed_version": ver,
                "url": f"https://github.com/pallets/flask/issues/{n}",
            },
        )

    items = []
    # 简单（5）
    items += [
        row(4024, "simple", "S", "2.0.1"),
        row(4020, "simple", "S", "2.0.1"),
        row(4040, "simple", "S", "2.0.1"),
        row(4044, "simple", "S", "2.0.1"),
        row(4295, "simple", "S", "2.0.3"),
    ]
    # 中等（15）
    items += [
        row(4019, "medium", "A", "2.0.1"),
        row(4041, "medium", "S", "2.0.1"),
        row(4078, "medium", "A", "2.0.1"),
        row(4060, "medium", "S", "2.0.1"),
        row(4069, "medium", "A", "2.0.1"),
        row(1091, "medium", "A", "2.0.1"),
        row(4093, "medium", "S", "2.0.2"),
        row(4104, "medium", "S", "2.0.2"),
        row(4098, "medium", "S", "2.0.2"),
        row(4095, "medium", "S", "2.0.2"),
        row(4124, "medium", "A", "2.0.2"),
        row(4150, "medium", "S", "2.0.2"),
        row(4157, "medium", "A", "2.0.2"),
        row(4096, "medium", "A", "2.0.2"),
        row(4170, "medium", "S", "2.0.2"),
    ]
    # 困难（5）
    items += [
        row(4037, "hard", "A", "2.0.1"),
        row(4053, "hard", "D", "2.0.1"),
        row(4112, "hard", "D", "2.0.2"),
        row(4229, "hard", "D", "2.0.2"),
        row(4333, "hard", "D", "2.0.3"),
    ]
    return dict(items)


def load_latest_report():
    """加载最新的检测报告（与 pandas 脚本相同策略）。"""
    reports_dir = Path("api/reports")
    if not reports_dir.exists():
        print("❌ 未找到报告目录: api/reports/")
        return None

    # 优先 bug_detection_report_*.json，其次 structured_*.json
    json_files = list(reports_dir.glob("bug_detection_report_*.json"))
    if not json_files:
        json_files = list(reports_dir.glob("structured_*.json"))
    if not json_files:
        print("❌ 未找到检测结果文件\n\n请先运行检测：\n  1. python start_api.py\n  2. 打开 frontend/index.html\n  3. 上传 Flask 源码或子目录 (src/flask)")
        return None

    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 分析报告: {latest.name}\n")
    try:
        with open(latest, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取报告失败: {e}")
        return None


def extract_detected_issue_ids(results):
    """从检测结果中提取被 Agent 识别到的 Flask Issue 号。

    兼容字段：issue_id / id / url；若均无则跳过。
    """
    issues = results.get("issues", [])
    detected = set()
    for it in issues:
        raw = it.get("issue_id") or it.get("id") or it.get("url") or ""
        iid = normalize_issue_id(raw)
        if iid:
            detected.add(iid)
    return detected


def compare_with_gold(detected_ids, gold):
    gold_ids = set(gold.keys())
    tp = sorted(gold_ids & detected_ids)
    missing = sorted(gold_ids - detected_ids)
    extra = sorted(detected_ids - gold_ids)

    precision = (len(tp) / (len(tp) + len(extra))) if (len(tp) + len(extra)) else 0.0
    recall = (len(tp) / (len(tp) + len(missing))) if (len(tp) + len(missing)) else 0.0

    return {
        "tp": tp,
        "missing": missing,
        "extra": extra,
        "precision": precision,
        "recall": recall,
        "f1": (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0,
    }


def generate_detailed_report(gold, comp):
    print("\n📊 详细Issue清单:")
    print("-" * 70)
    for iid, meta in gold.items():
        status = "✅" if iid in comp["tp"] else ("❌" if iid in comp["missing"] else "⭕")
        print(f"{status} {iid:12s} | {meta['difficulty']:6s} | cap={meta['capability']} | fixed={meta['fixed_version']}\n   {meta['url']}")
    print("-" * 70)


def main():
    print("\n" + "=" * 70)
    print("     Flask 2.0.0 Issue 检测对比分析（25条）")
    print("=" * 70 + "\n")

    gold = embedded_gold()
    results = load_latest_report()
    if not results:
        return

    detected_ids = extract_detected_issue_ids(results)

    # 概览（保持输出风格与 pandas 对齐）
    issues = results.get('issues', [])
    summary = results.get('summary', {})
    print(f"检测到的问题总数: {len(issues)}")
    print(f"  - 错误: {summary.get('error_count', 0)}")
    print(f"  - 警告: {summary.get('warning_count', 0)}")
    print(f"  - 信息: {summary.get('info_count', 0)}\n")

    # 对比
    comp = compare_with_gold(detected_ids, gold)

    print("=" * 70)
    print("   Flask 2.0.0 检测结果对比（扩展版 - 25个Issue）")
    print("=" * 70)
    print()

    print("已知Issue vs 系统检测:")
    print("-" * 70)
    print(f"  命中 (TP): {len(comp['tp'])}")
    print(f"  缺失 (FN): {len(comp['missing'])}")
    print(f"  多报 (FP): {len(comp['extra'])}")
    print()

    print("-" * 70)
    print(f"总体 Precision: {comp['precision']:.3f}")
    print(f"总体 Recall   : {comp['recall']:.3f}")
    print(f"总体 F1       : {comp['f1']:.3f}")
    print()

    generate_detailed_report(gold, comp)

    # 保存报告
    output_file = "flask_comparison_report.json"
    out = {
        "precision": round(comp["precision"], 4),
        "recall": round(comp["recall"], 4),
        "f1": round(comp["f1"], 4),
        "tp": comp["tp"],
        "missing": comp["missing"],
        "extra": comp["extra"],
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 详细报告已保存: {output_file}")

    # 总结
    print("\n" + "=" * 70)
    print("  总结")
    print("=" * 70)
    print(f"总体 Precision: {comp['precision']:.1%}")
    print(f"总体 Recall   : {comp['recall']:.1%}")
    print(f"总体 F1       : {comp['f1']:.1%}")
    print("\n说明：")
    print("- 本对比脚本与 Pandas 版保持相同的输出结构，便于前端统一展示")
    print("- 金标为 2.0.1/2.0.2/2.0.3 修复、2.0.0 存在的 25 条 Issue（内置）")
    print("- 建议配合上传的检测结果，在 api/reports 中自动读取最新 JSON")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


