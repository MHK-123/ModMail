import asyncio
import base64
import io
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from playwright.async_api import async_playwright

app = FastAPI(title="DungeonKeeper Image Service")

class ShipRequest(BaseModel):
    av1_url: str
    av2_url: str
    name1: str
    name2: str
    percentage: int


def build_html(av1_b64: str, av2_b64: str, name1: str, name2: str, percentage: int) -> str:
    av1_uri = f"data:image/png;base64,{av1_b64}"
    av2_uri = f"data:image/png;base64,{av2_b64}"
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    width: 900px;
    height: 380px;
    background: #0a0c1c;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    overflow: hidden;
  }}

  .card {{
    position: relative;
    width: 860px;
    height: 340px;
    border-radius: 24px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(20px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 30px 40px;
  }}

  .glow-pink {{
    position: absolute; width: 500px; height: 500px; border-radius: 50%;
    background: radial-gradient(circle, rgba(236,72,153,0.4) 0%, transparent 70%);
    top: -200px; left: -150px; filter: blur(50px); pointer-events: none;
  }}
  .glow-blue {{
    position: absolute; width: 500px; height: 500px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.4) 0%, transparent 70%);
    bottom: -200px; right: -150px; filter: blur(50px); pointer-events: none;
  }}
  .glow-purple {{
    position: absolute; width: 400px; height: 400px; border-radius: 50%;
    background: radial-gradient(circle, rgba(168,85,247,0.25) 0%, transparent 70%);
    top: 50%; left: 50%; transform: translate(-50%,-50%);
    filter: blur(60px); pointer-events: none;
  }}

  .header {{ position: relative; z-index: 2; margin-bottom: 6px; }}
  .title {{ font-size: 28px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }}
  .title span {{ color: #ec4899; }}
  .subtitle {{ font-size: 16px; color: rgba(255,255,255,0.6); margin-top: 4px; }}
  .subtitle strong {{ color: rgba(255,255,255,0.95); font-weight: 600; }}
  .subtitle .pct {{ color: #ec4899; font-weight: 700; }}

  .row {{
    position: relative; z-index: 2;
    display: flex; align-items: center;
    justify-content: space-between; flex: 1; margin-top: 10px;
  }}

  .connector {{
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%; pointer-events: none;
  }}

  .avatar-wrap {{ display: flex; flex-direction: column; align-items: center; gap: 8px; }}
  .avatar {{ width: 160px; height: 160px; border-radius: 50%; object-fit: cover; display: block; }}
  .avatar-left  {{ box-shadow: 0 0 0 3px #ec4899, 0 0 28px 10px rgba(236,72,153,0.55); }}
  .avatar-right {{ box-shadow: 0 0 0 3px #3b82f6, 0 0 28px 10px rgba(59,130,246,0.55); }}
  .avatar-name {{ font-size: 13px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }}
  .avatar-name-left  {{ color: #ec4899; }}
  .avatar-name-right {{ color: #3b82f6; }}

  .heart-wrap {{ display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .heart {{
    position: relative; width: 120px; height: 110px;
    filter: drop-shadow(0 0 20px rgba(236,72,153,1)) drop-shadow(0 0 50px rgba(236,72,153,0.6));
  }}
  .heart::before, .heart::after {{
    content: ""; position: absolute; left: 60px; top: 0;
    width: 60px; height: 96px;
    background: linear-gradient(135deg, #f472b6, #ec4899, #be185d);
    border-radius: 60px 60px 0 0; transform-origin: 0 100%;
  }}
  .heart::before {{ transform: rotate(-45deg); }}
  .heart::after {{ left: 0; transform-origin: 100% 100%; transform: rotate(45deg); }}
  .heart-pct {{
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -40%);
    font-size: 22px; font-weight: 800; color: #fff;
    text-shadow: 0 1px 4px rgba(0,0,0,0.7);
    z-index: 5; white-space: nowrap;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="glow-pink"></div>
  <div class="glow-blue"></div>
  <div class="glow-purple"></div>

  <div class="header">
    <div class="title">&#10084;&#65039; Compatibility <span>Match</span></div>
    <div class="subtitle">
      <strong>{name1}</strong> and <strong>{name2}</strong> are a <span class="pct">{percentage}%</span> match!
    </div>
  </div>

  <div class="row">
    <svg class="connector" viewBox="0 0 780 180" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M 160 90 Q 350 20 390 90" stroke="url(#gl)" stroke-width="2" opacity="0.7"/>
      <path d="M 620 90 Q 430 20 390 90" stroke="url(#gr)" stroke-width="2" opacity="0.7"/>
      <defs>
        <linearGradient id="gl" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#ec4899"/>
          <stop offset="100%" stop-color="#a855f7"/>
        </linearGradient>
        <linearGradient id="gr" x1="1" y1="0" x2="0" y2="0">
          <stop offset="0%" stop-color="#3b82f6"/>
          <stop offset="100%" stop-color="#a855f7"/>
        </linearGradient>
      </defs>
    </svg>

    <div class="avatar-wrap">
      <img class="avatar avatar-left" src="{av1_uri}" />
      <span class="avatar-name avatar-name-left">{name1}</span>
    </div>

    <div class="heart-wrap">
      <div class="heart">
        <span class="heart-pct">{percentage}%</span>
      </div>
    </div>

    <div class="avatar-wrap">
      <img class="avatar avatar-right" src="{av2_uri}" />
      <span class="avatar-name avatar-name-right">{name2}</span>
    </div>
  </div>
</div>
</body>
</html>"""


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ship")
async def ship(req: ShipRequest):
    # Download avatars
    async with aiohttp.ClientSession() as session:
        async with session.get(req.av1_url) as r1, session.get(req.av2_url) as r2:
            if r1.status != 200 or r2.status != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch avatars")
            av1_b64 = base64.b64encode(await r1.read()).decode()
            av2_b64 = base64.b64encode(await r2.read()).decode()

    html = build_html(av1_b64, av2_b64, req.name1, req.name2, req.percentage)

    # Render with Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = await browser.new_page(viewport={"width": 900, "height": 380})
        await page.set_content(html, wait_until="networkidle")
        png_bytes = await page.locator(".card").screenshot()
        await browser.close()

    return Response(content=png_bytes, media_type="image/png")
