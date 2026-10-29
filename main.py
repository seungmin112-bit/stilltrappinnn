
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="0교시 | 학교가 너를 기억한다",
    page_icon="👁️",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: #080b12;
    color: #e5e7eb;
}
h1, h2, p, label {
    color: #e5e7eb !important;
}
.block-container {
    padding-top: 1.2rem;
    max-width: 1100px;
}
</style>
""", unsafe_allow_html=True)

st.title("👁️ 0교시 — 학교가 너를 기억한다")
st.caption("00:13 AM · 야간 학교 탈출 기록 #001")

st.markdown("""
**임무:** 학교 정문을 열고 탈출하라.

- `W A S D` 또는 방향키: 이동
- `Shift`: 달리기 (소음 증가)
- `E`: 주변 아이템 줍기 / 문 상호작용
- `F`: 손전등 켜기 / 끄기
- 괴물은 소리를 듣고 마지막 위치를 조사한다.
""")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #080b12;
  color: #e5e7eb;
  font-family: system-ui, sans-serif;
}
#wrap { max-width: 840px; margin: auto; padding: 8px; }
#hud {
  display: flex; flex-wrap: wrap; gap: 8px;
  justify-content: space-between; margin-bottom: 10px;
}
.pill {
  background: #151b27; border: 1px solid #343c4d;
  padding: 8px 12px; border-radius: 8px; font-size: 13px;
}
#game {
  display: block; width: 100%; height: auto;
  border: 2px solid #343c4d; border-radius: 8px;
  background: #0b0e15; outline: none;
}
#message {
  min-height: 42px; padding: 10px 12px; margin-top: 10px;
  background: #151b27; border-left: 3px solid #8b5cf6;
  border-radius: 4px; font-size: 14px;
}
#help { color: #9ca3af; font-size: 12px; margin-top: 8px; }
button {
  cursor: pointer; color: white; background: #713f9e;
  border: 0; border-radius: 8px; padding: 9px 14px;
  font-weight: bold;
}
#overlay {
  position: absolute; inset: 0; display: flex;
  flex-direction: column; align-items: center; justify-content: center;
  background: #05070bea; text-align: center; padding: 24px;
}
#overlay h1 { color: #e9d5ff; font-size: clamp(24px, 5vw, 42px); }
#overlay p { max-width: 420px; line-height: 1.8; color: #cbd5e1; }
#stage { position: relative; }
</style>
</head>
<body>
<div id="wrap">
  <div id="hud">
    <div class="pill" id="clock">🕛 00:13</div>
    <div class="pill" id="items">🔑 열쇠: 0/1 · 퓨즈: 0/1</div>
    <div class="pill" id="noise">🔊 소음: 낮음</div>
    <div class="pill" id="status">👁️ 무언가 깨어 있다</div>
  </div>
  <div id="stage">
    <canvas id="game" width="800" height="560" tabindex="0"></canvas>
    <div id="overlay">
      <h1>0교시</h1>
      <p>학교는 비어 있어야 한다.<br>그런데 복도 저편에서 네 이름을 부르는 소리가 들린다.</p>
      <p>열쇠와 퓨즈를 찾아 정문으로 탈출해.<br>괴물은 네가 남긴 소리를 기억한다.</p>
      <button id="start">학교에 들어가기</button>
    </div>
  </div>
  <div id="message">복도에 들어가기 전, 주변을 살펴보자.</div>
  <div id="help">
    이동: WASD / 방향키 · 달리기: Shift · 상호작용: E · 손전등: F
    <br>게임 화면을 한 번 클릭한 뒤 키보드를 사용하세요.
  </div>
</div>

<script>
(() => {
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const W = 20, H = 14, T = 40;
const msg = document.getElementById("message");
const overlay = document.getElementById("overlay");

let map, player, monster, items, keys, running, won, lost;
let flashlight, noise, elapsed, lastTime, monsterTick, memory, path;
let keysDown = {};
let seenRoutes = {};
let footsteps = 0;
let messageTimer = 0;

function makeMap() {
  const a = Array.from({length:H}, (_,y) =>
    Array.from({length:W}, (_,x) =>
      x===0 || y===0 || x===W-1 || y===H-1 ? "#" : "."
    )
  );

  // 학교의 벽과 복도
  for(let y=1;y<=3;y++) a[y][6]="#";
  for(let y=1;y<=3;y++) a[y][13]="#";
  for(let x=1;x<=4;x++) a[5][x]="#";
  for(let x=8;x<=11;x++) a[5][x]="#";
  for(let x=14;x<=18;x++) a[5][x]="#";
  for(let y=7;y<=10;y++) a[y][4]="#";
  for(let y=7;y<=11;y++) a[y][15]="#";
  for(let x=7;x<=11;x++) a[9][x]="#";
  // 정문과 교실 통로
  a[1][18]="E";
  a[2][17]="K";
  a[11][2]="F";
  return a;
}

function reset() {
  map = makeMap();
  player = {x:1.5*T, y:1.5*T, r:10, speed:145};
  monster = {x:10.5*T, y:8.5*T, speed:67, state:"wander"};
  items = {key:false, fuse:false};
  keys = {key:false, fuse:false};
  running = true; won = false; lost = false;
  flashlight = true; noise = 0; elapsed = 0;
  lastTime = performance.now(); monsterTick = 0;
  memory = {x:player.x, y:player.y, time:0};
  path = []; seenRoutes = {}; footsteps = 0;
  say("발소리가 들린다. 정문까지 가야 한다.");
  overlay.style.display = "none";
  canvas.focus();
}

function say(text) {
  msg.textContent = text;
  messageTimer = 3;
}

function tileAt(px, py) {
  const x = Math.floor(px/T), y = Math.floor(py/T);
  if(x<0 || x>=W || y<0 || y>=H) return "#";
  return map[y][x];
}

function blocked(px, py, radius=8) {
  return tileAt(px-radius,py-radius)==="#" ||
         tileAt(px+radius,py-radius)==="#" ||
         tileAt(px-radius,py+radius)==="#" ||
         tileAt(px+radius,py+radius)==="#";
}

function moveEntity(ent, dx, dy, radius=8) {
  if(!blocked(ent.x+dx,ent.y,radius)) ent.x += dx;
  if(!blocked(ent.x,ent.y+dy,radius)) ent.y += dy;
}

function cell(x,y) { return `${Math.floor(x/T)},${Math.floor(y/T)}`; }

function findPath(sx, sy, tx, ty) {
  const start=[Math.floor(sx/T),Math.floor(sy/T)];
  const end=[Math.floor(tx/T),Math.floor(ty/T)];
  const q=[start], prev=new Map();
  const id=(x,y)=>`${x},${y}`;
  prev.set(id(...start),null);
  const dirs=[[1,0],[-1,0],[0,1],[0,-1]];
  while(q.length) {
    const [x,y]=q.shift();
    if(x===end[0] && y===end[1]) break;
    for(const [dx,dy] of dirs) {
      const nx=x+dx, ny=y+dy, k=id(nx,ny);
      if(nx<0||ny<0||nx>=W||ny>=H||map[ny][nx]==="#"||prev.has(k)) continue;
      prev.set(k,id(x,y)); q.push([nx,ny]);
    }
  }
  const endId=id(...end);
  if(!prev.has(endId)) return [];
  const out=[]; let cur=endId;
  while(cur!==null) {
    const [x,y]=cur.split(",").map(Number);
    out.push({x:(x+.5)*T,y:(y+.5)*T});
    cur=prev.get(cur);
  }
  return out.reverse().slice(1);
}

function interact() {
  if(!running) return;
  const cx=Math.floor(player.x/T), cy=Math.floor(player.y/T);
  let found=false;
  for(let y=cy-1;y<=cy+1;y++) for(let x=cx-1;x<=cx+1;x++) {
    if(!map[y] || map[y][x]===undefined) continue;
    const tile=map[y][x];
    const dist=Math.hypot(player.x-(x+.5)*T,player.y-(y+.5)*T);
    if(dist>58) continue;
    if(tile==="K"&&!items.key) {
      items.key=true; map[y][x]=".";
      say("🔑 교무실 열쇠를 찾았다. 어딘가의 문이 열릴 것이다.");
      found=true;
    }
    if(tile==="F"&&!items.fuse) {
      items.fuse=true; map[y][x]=".";
      say("⚡ 퓨즈를 찾았다. 정문 전력을 복구할 수 있다.");
      found=true;
    }
    if(tile==="E") {
      if(items.key && items.fuse) {
        running=false; won=true; finish(true);
      } else {
        say("정문은 잠겨 있다. 열쇠와 퓨즈가 필요하다.");
        found=true;
      }
    }
  }
  if(!found) say("주변에는 아무것도 없다.");
}

function finish(win) {
  running=false;
  overlay.style.display="flex";
  overlay.innerHTML = win
    ? `<h1>탈출 성공</h1><p>정문이 열렸다.<br>뒤를 돌아보는 순간, CCTV 화면 속 네 모습이 웃고 있다.</p><p>생존 시간: ${Math.floor(elapsed)}초</p><button id="again">다시 플레이</button>`
    : `<h1>너를 기억한다</h1><p>발소리가 멈췄다.<br>다음 날, 교실 출석부에 네 이름이 새로 적혀 있었다.</p><p>생존 시간: ${Math.floor(elapsed)}초</p><button id="again">다시 도전</button>`;
  document.getElementById("again").onclick=reset;
}

function update(dt) {
  if(!running) return;
  elapsed += dt;
  monsterTick += dt;
  memory.time += dt;
  if(messageTimer>0) messageTimer-=dt;

  let dx=0,dy=0;
  if(keysDown["ArrowLeft"]||keysDown["a"]) dx--;
  if(keysDown["ArrowRight"]||keysDown["d"]) dx++;
  if(keysDown["ArrowUp"]||keysDown["w"]) dy--;
  if(keysDown["ArrowDown"]||keysDown["s"]) dy++;

  const moving=dx!==0||dy!==0;
  const sprint=keysDown["Shift"] && moving;
  const speed=player.speed*(sprint?1.65:1);
  if(moving) {
    const len=Math.hypot(dx,dy); dx/=len; dy/=len;
    moveEntity(player,dx*speed*dt,dy*speed*dt,9);
    footsteps += dt*(sprint?2.4:0.65);
    if(footsteps>=1) {
      footsteps=0;
      const c=cell(player.x,player.y);
      seenRoutes[c]=(seenRoutes[c]||0)+1;
      if(sprint) {
        noise=100;
        memory={x:player.x,y:player.y,time:0};
      } else {
        noise=Math.max(noise,30);
        if(Math.random()<0.25) memory={x:player.x,y:player.y,time:0};
      }
    }
  }
  noise=Math.max(0,noise-22*dt);

  // 괴물은 소리를 조사하고, 이후 플레이어를 추적한다.
  const dist=Math.hypot(player.x-monster.x,player.y-monster.y);
  if(noise>45 && dist<330) {
    monster.state="investigate";
  } else if(dist<175) {
    monster.state="chase";
  } else if(monster.state==="chase" && dist>300) {
    monster.state="wander";
  }

  if(monsterTick>0.12) {
    monsterTick=0;
    let target;
    if(monster.state==="investigate") target={x:memory.x,y:memory.y};
    else if(monster.state==="chase") target={x:player.x,y:player.y};
    else {
      target={x:(2+Math.random()*15)*T,y:(2+Math.random()*9)*T};
      if(Math.random()<0.7) target={x:player.x,y:player.y};
    }
    path=findPath(monster.x,monster.y,target.x,target.y);
  }

  if(path.length) {
    const p=path[0];
    const vx=p.x-monster.x, vy=p.y-monster.y;
    const len=Math.hypot(vx,vy);
    if(len<5) path.shift();
    else {
      const sp=monster.speed*(monster.state==="chase"?1.7:1);
      moveEntity(monster,vx/len*sp*dt,vy/len*sp*dt,9);
    }
  }

  if(dist<18) finish(false);
  if(elapsed>300) {
    running=false; finish(false);
  }

  document.getElementById("clock").textContent="🕛 "+String(Math.floor(elapsed/60)).padStart(2,"0")+":"+String(Math.floor(elapsed%60)).padStart(2,"0");
  document.getElementById("items").textContent=`🔑 열쇠: ${items.key?1:0}/1 · 퓨즈: ${items.fuse?1:0}/1`;
  document.getElementById("noise").textContent="🔊 소음: "+(noise>65?"위험":noise>25?"보통":"낮음");
  document.getElementById("status").textContent=monster.state==="chase"?"🚨 추적당하는 중!":monster.state==="investigate"?"👂 소리를 조사 중":"👁️ 무언가 배회 중";
}

function draw() {
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for(let y=0;y<H;y++) for(let x=0;x<W;x++) {
    const t=map[y][x], px=x*T, py=y*T;
    ctx.fillStyle=t==="#"?"#252b37":"#111722";
    ctx.fillRect(px,py,T-1,T-1);
    if(t==="#") {
      ctx.fillStyle="#343b49"; ctx.fillRect(px+2,py+2,T-5,4);
    } else {
      ctx.strokeStyle="#1b2431"; ctx.strokeRect(px,py,T,T);
    }
    if(t==="K") { ctx.font="24px sans-serif";ctx.fillText("🔑",px+7,py+29); }
    if(t==="F") { ctx.font="24px sans-serif";ctx.fillText("🔋",px+7,py+29); }
    if(t==="E") { ctx.fillStyle="#166534";ctx.fillRect(px+3,py+3,T-7,T-7);ctx.font="23px sans-serif";ctx.fillText("🚪",px+7,py+29); }
  }

  // 손전등 시야
  ctx.save();
  ctx.fillStyle="rgba(0,0,0,0.88)";
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.globalCompositeOperation="destination-out";
  const radius=flashlight?155:75;
  const grad=ctx.createRadialGradient(player.x,player.y,12,player.x,player.y,radius);
  grad.addColorStop(0,"rgba(0,0,0,1)");
  grad.addColorStop(1,"rgba(0,0,0,0)");
  ctx.fillStyle=grad;
  ctx.beginPath();ctx.arc(player.x,player.y,radius,0,Math.PI*2);ctx.fill();
  ctx.restore();

  // 플레이어
  ctx.fillStyle="#67e8f9";
  ctx.beginPath();ctx.arc(player.x,player.y,9,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle="#cffafe";ctx.lineWidth=2;ctx.stroke();

  // 괴물은 가까이 있거나 추적할 때 더 선명하게 보임
  const d=Math.hypot(player.x-monster.x,player.y-monster.y);
  if(d<240 || monster.state==="chase") {
    ctx.save();
    ctx.shadowColor="#ef4444";ctx.shadowBlur=18;
    ctx.fillStyle="#991b1b";
    ctx.beginPath();ctx.arc(monster.x,monster.y,11,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#fecaca";
    ctx.fillRect(monster.x-5,monster.y-3,3,3);
    ctx.fillRect(monster.x+3,monster.y-3,3,3);
    ctx.restore();
  }

  if(!flashlight) {
    ctx.fillStyle="#e5e7eb";ctx.font="12px sans-serif";
    ctx.fillText("손전등 OFF",12,20);
  }
}

function loop(now) {
  const dt=Math.min((now-lastTime)/1000,0.05);
  lastTime=now;
  update(dt);
  draw();
  requestAnimationFrame(loop);
}

window.addEventListener("keydown",e=>{
  const k=e.key.length===1?e.key.toLowerCase():e.key;
  if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(k)) e.preventDefault();
  keysDown[k]=true;
  if(e.repeat) return;
  if(k==="e") interact();
  if(k==="f") {flashlight=!flashlight;say(flashlight?"손전등을 켰다.":"손전등을 껐다.");}
});
window.addEventListener("keyup",e=>{
  const k=e.key.length===1?e.key.toLowerCase():e.key;
  keysDown[k]=false;
});
window.addEventListener("blur",()=>{keysDown={};});
document.getElementById("start").onclick=reset;

reset();
overlay.style.display="flex";
overlay.innerHTML=`<h1>0교시</h1><p>00:13 AM<br>학교가 비어 있어야 한다.<br>그런데 누군가 네 이름을 부른다.</p><p>열쇠와 퓨즈를 찾아 정문으로 탈출해.<br>달리면 괴물이 소리를 듣는다.</p><button id="start">학교에 들어가기</button>`;
document.getElementById("start").onclick=reset;
requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

components.html(game_html, height=790, scrolling=False)

st.caption(
    "프로토타입: 게임 화면은 브라우저 안에서 실행됩니다. "
    "새로고침하면 게임 진행이 초기화됩니다."
)
