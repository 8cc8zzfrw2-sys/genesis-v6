# Architect Genesis AI v6

「ファイルを表示して使うAI」から「アプリを開いて使うAI」へ変更したプロトタイプです。

## 構成
- **Architect Core**: 意図理解・計画・判断・評価
- **AI OS**: 外部機能をツールとして管理し、将来ここから実機能へ接続
- **PWA**: iPhone/PCのブラウザからアプリとして起動可能
- **Project Store**: 設計・アップデート履歴を裏側のJSONに保存

## 外部ツールの入口
`/tools` にカメラ、マイク、OCR、GPS、検索、翻訳、3D、PC操作などを登録済み。
現段階では安全な「ツール定義」までで、各実機能の接続は個別実装が必要です。

## 起動
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="あなたのAPIキー"
uvicorn app:app --host 0.0.0.0 --port 8000
```
Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="あなたのAPIキー"
uvicorn app:app --host 0.0.0.0 --port 8000
```

ブラウザでサーバーのURLを開き、ホーム画面へ追加するとPWAとして使えます。

## 次の実装
1. AI OSのtool_callを実際のコネクター実行へ接続
2. iPhoneカメラ/マイク/GPSからPCの司令塔へデータ送信
3. 権限確認・ログ・認証
4. OCR、検索、翻訳、3D、PC操作を追加
5. 隔離環境で自動テスト→修正→再テスト
