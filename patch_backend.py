from pathlib import Path
p = None
for name in ("app.py","monolit.py"):
    f = Path("/workspace/mrd")/name
    if f.exists():
        p=f; break
if p is None:
    p = Path("/workspace/mrd/app.py")
    p.write_text("from fastapi import FastAPI\napp=FastAPI()\n")

txt = p.read_text()
if "FastAPI" not in txt:
    txt = "from fastapi import FastAPI\napp=FastAPI()\n" + txt
if '@app.get("/")' not in txt:
    txt += "\nfrom fastapi.responses import PlainTextResponse\n@app.get('/')\ndef root():\n    return PlainTextResponse('Mordzix API działa')\n"
p.write_text(txt)
print("patched", p)
