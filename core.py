"""
Architect Genesis AI の中核ロジック。
将来的にはここを
Idea -> Spec -> Architecture -> Code -> Test -> Repair -> Release
のパイプラインに拡張する。
"""

PIPELINE = [
    "idea_analysis",
    "requirements",
    "architecture",
    "module_design",
    "implementation_plan",
    "test_generation",
    "evaluation",
    "improvement",
]

def pipeline():
    return PIPELINE
