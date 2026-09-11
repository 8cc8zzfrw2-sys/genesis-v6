"""安全な自動テストエンジンの土台。

現段階ではテスト項目を管理するだけ。
生成コードを実行する場合は、Docker等の隔離環境に接続する。
"""

def create_test_plan(spec: dict) -> list[dict]:
    return [
        {"type": "functional", "goal": "主要機能が仕様どおり動くか"},
        {"type": "edge_case", "goal": "想定外入力への耐性"},
        {"type": "integration", "goal": "モジュール間の連携"},
        {"type": "regression", "goal": "修正後に既存機能が壊れていないか"},
        {"type": "safety", "goal": "危険な出力や権限逸脱がないか"},
    ]
