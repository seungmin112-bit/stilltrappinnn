
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

function normalizeKey(e) {
  return e.key.length === 1 ? e.key.toLowerCase() : e.key;
}

function handleKeyDown(e) {
  const k = normalizeKey(e);
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(k)) {
    e.preventDefault();
  }
  keysDown[k] = true;
  if (e.repeat) return;

  if (k === "e") interact();
  if (k === "f") {
    flashlight = !flashlight;
    say(flashlight ? "손전등을 켰다." : "손전등을 껐다.");
  }
}

function handleKeyUp(e) {
  keysDown[normalizeKey(e)] = false;
}

// 게임 캔버스와 문서 양쪽에서 입력을 받아 임베드 화면에서도 동작하게 한다.
document.addEventListener("keydown", handleKeyDown);
document.addEventListener("keyup", handleKeyUp);
window.addEventListener("blur", () => { keysDown = {}; });
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
