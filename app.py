import os, json, uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

APP_VERSION = "6.0.0"
app = FastAPI(title="Architect Genesis AI", version=APP_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
DATA = Path(os.getenv("ARCHITECT_DATA_DIR", "architect_projects")); DATA.mkdir(exist_ok=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

SYSTEM = """あなたはArchitect Genesis AIの思考コアです。あなたの役割は、ユーザーの意図を理解し、目的を分解し、必要な外部機能を選び、実行順序を決め、結果を評価して改善することです。
あなた自身がカメラ等を直接持つのではなく、AI OSが提供するツールを司令します。
必ずJSONで返してください。キー:
intent, goal, assumptions, plan, tool_calls, final_answer, risks, next_actions, version
planは順序付き配列。tool_callsは {"tool":"...","reason":"...","input":{}} の配列。
"""

TOOLS = {
    "camera": "スマートフォン等のカメラ映像を取得する外部入力",
    "microphone": "音声を取得する外部入力",
    "speech_to_text": "音声を文字に変換",
    "ocr": "画像から文字を読み取る",
    "gps": "位置情報を取得",
    "web_search": "Web情報を検索",
    "translation": "翻訳",
    "file": "ファイルの読み書き",
    "code_runner": "隔離環境でコードをテスト",
    "3d": "3Dモデル・設計データ生成",
    "pc_control": "許可されたPC操作",
}

class ChatRequest(BaseModel):
    message: str
    context: dict[str, Any] = {}
    available_tools: list[str] | None = None

class DesignRequest(BaseModel): idea: str
class UpdateRequest(BaseModel): project_id: str; request: str


def fallback(prompt: str):
    return {"intent":"要望の理解","goal":prompt,"assumptions":[],"plan":["意図を解析","必要機能を選択","実行","結果を評価"],"tool_calls":[],"final_answer":"OPENAI_API_KEYが設定されていないため、思考コアの接続待ちです。","risks":["AI API未接続"],"next_actions":["OPENAI_API_KEYを設定"],"version":APP_VERSION}

def ask(prompt: str, tools: dict | None = None):
    if not client: return fallback(prompt)
    tool_text = json.dumps(tools or TOOLS, ensure_ascii=False)
    r = client.chat.completions.create(model=os.getenv("ARCHITECT_MODEL", "gpt-5"), response_format={"type":"json_object"}, messages=[{"role":"system","content":SYSTEM + "\n利用可能ツール:\n" + tool_text},{"role":"user","content":prompt}])
    return json.loads(r.choices[0].message.content)

def save_project(pid, data): (DATA / f"{pid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def load_project(pid):
    p=DATA/f"{pid}.json"
    if not p.exists(): raise HTTPException(404,"project not found")
    return json.loads(p.read_text(encoding="utf-8"))

def bump(v):
    try:
        a,b,c=[int(x) for x in v.split(".")[:3]]; return f"{a}.{b+1}.0"
    except Exception: return "1.1.0"

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(open(Path(__file__).parent/"static"/"index.html", encoding="utf-8").read())

@app.get("/manifest.webmanifest")
def manifest():
    return JSONResponse({"name":"Architect Genesis AI","short_name":"Architect","start_url":"/","scope":"/","display":"standalone","background_color":"#0b0d10","theme_color":"#0b0d10","description":"思考AI + AI OS 司令塔"})

@app.get("/sw.js")
def sw():
    return HTMLResponse("""const CACHE='architect-6';self.addEventListener('install',e=>{self.skipWaiting()});self.addEventListener('activate',e=>e.waitUntil(clients.claim()));self.addEventListener('fetch',e=>{if(e.request.method==='GET'){e.respondWith(caches.match(e.request).then(x=>x||fetch(e.request).then(r=>{const c=r.clone();caches.open(CACHE).then(k=>k.put(e.request,c));return r}).catch(()=>caches.match('/'))))}});""", media_type="application/javascript")

@app.get("/health")
def health(): return {"status":"ok","service":"Architect Genesis AI","version":APP_VERSION,"core_connected":client is not None}

@app.get("/tools")
def tools(): return {"tools":TOOLS}

@app.post("/chat")
def chat(req: ChatRequest):
    allowed={k:v for k,v in TOOLS.items() if not req.available_tools or k in req.available_tools}
    prompt=f"ユーザー入力:\n{req.message}\n\n現在の外部コンテキスト:\n{json.dumps(req.context,ensure_ascii=False)}"
    result=ask(prompt,allowed); result["timestamp"]=datetime.now().isoformat(); return result

@app.post("/architect")
def architect(req: DesignRequest):
    result=ask("新しいAIを設計してください。ユーザー要望:\n"+req.idea)
    pid=str(uuid.uuid4()); result.update(project_id=pid,created_at=datetime.now().isoformat(),version=result.get("version") or "1.0.0"); save_project(pid,result); return result

@app.post("/update")
def update(req: UpdateRequest):
    current=load_project(req.project_id)
    result=ask("既存AIをアップデート。現在仕様:\n"+json.dumps(current,ensure_ascii=False)+"\n変更要望:\n"+req.request)
    result.update(project_id=req.project_id,previous_version=current.get("version","1.0.0"),version=bump(current.get("version","1.0.0")),updated_at=datetime.now().isoformat()); save_project(req.project_id,result); return result

@app.post("/save")
def save(req: dict):
    pid=req.get("project_id") or str(uuid.uuid4()); req["project_id"]=pid; save_project(pid,req); return {"project_id":pid}

@app.get("/project/{project_id}")
def project(project_id:str): return load_project(project_id)
