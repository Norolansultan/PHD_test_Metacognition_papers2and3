"use strict";
/* White-cell control display.
   Ground truth, blue's believed picture, and the gap between them — which is the
   thing the people portraying the situation actually need to see.

   The reference is a constructive commander simulator: APP-6 style symbols,
   plotted courses with heading and speed, weapon and sensor reach, a clock with
   time acceleration, and a message log that fills as the situation develops. */

const params = new URLSearchParams(location.search);
const PID = params.get("pid") || "wc001";
const SCENARIO = params.get("scenario") || "fin-def-03";

const $ = id => document.getElementById(id);
const cv = $("map"), ctx = cv.getContext("2d");
const TERRAIN_COLOUR = {open:"#2E3A2C", forest:"#1F3020", water:"#16303F",
                        road:"#4A4030", urban:"#3A3830", track:"#3A3526"};
const SIDE = {blue:"#5B9BD5", red:"#E05A47", neutral:"#8593A2"};

let meta = null, terrainImg = null, truth = null, selected = null, rate = 0, timer = null;

/* Two transports, one display. Live it talks to the API; baked it steps through
   frames recorded from a real run, so the page can be handed to someone without
   a server. The rendering code cannot tell the difference. */
const REPLAY = window.REPLAY || null;
let frame = 0;

async function post(path, body){
  if (REPLAY){
    if (path === "/api/tick_n") frame = Math.min(REPLAY.frames.length - 1,
                                                 frame + (body.n || 1));
    return REPLAY.frames[frame];
  }
  const r = await fetch(path, {method:"POST", headers:{"Content-Type":"application/json"},
                              body: JSON.stringify(Object.assign({pid:PID}, body||{}))});
  return r.json();
}
const fmt = s => `${Math.floor(s/60)}:${String(s%60).padStart(2,"0")}`;

/* ---------------------------------------------------------------- canvas --- */

function fit(){
  const r = cv.parentElement.getBoundingClientRect();
  const d = window.devicePixelRatio || 1;
  cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d);
  ctx.setTransform(d, 0, 0, d, 0, 0);
  draw();
}
addEventListener("resize", fit);

function box(){
  const w = cv.width / (window.devicePixelRatio || 1);
  const h = cv.height / (window.devicePixelRatio || 1);
  const side = Math.min(w, h);
  return {ox:(w - side)/2, oy:(h - side)/2, side};
}
const P = p => { const b = box();
  return [b.ox + (p[0]/meta.width_m)*b.side, b.oy + (p[1]/meta.width_m)*b.side]; };
const M = m => (box().side / meta.width_m) * m;

/* Flat blocks of colour do not read as ground. Two cheap things fix most of it:
   deterministic tonal variation per cell so land cover has texture, and a shade
   on the north-west edge of every cover boundary so the eye reads relief. */
function hash2(x, y){
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}

function paintTerrain(){
  const img = new Image();
  img.onload = () => {
    const w = img.width, h = img.height;
    const src = document.createElement("canvas");
    src.width = w; src.height = h;
    const sg = src.getContext("2d"); sg.drawImage(img,0,0);
    const cls = sg.getImageData(0,0,w,h).data;
    const klass = (x,y) => meta.legend[String(cls[((Math.min(h-1,Math.max(0,y))*w)
                    + Math.min(w-1,Math.max(0,x)))*4])] || "open";

    const off = document.createElement("canvas");
    off.width = w; off.height = h;
    const g = off.getContext("2d");
    const out = g.createImageData(w,h);
    for (let y=0;y<h;y++) for (let x=0;x<w;x++){
      const k = klass(x,y);
      const c = TERRAIN_COLOUR[k] || TERRAIN_COLOUR.open;
      let r = parseInt(c.slice(1,3),16), gg = parseInt(c.slice(3,5),16),
          b = parseInt(c.slice(5,7),16);
      // Texture: land cover is never one flat tone.
      const n = (hash2(x,y) - 0.5) * (k === "water" ? 10 : 26);
      // Relief: darken where cover changes to the north-west, lighten to the south-east.
      const edge = (klass(x-1,y) !== k ? -14 : 0) + (klass(x,y-1) !== k ? -14 : 0)
                 + (klass(x+1,y) !== k ?   8 : 0) + (klass(x,y+1) !== k ?   8 : 0);
      const i = (y*w + x) * 4;
      out.data[i]   = Math.max(0, Math.min(255, r  + n + edge));
      out.data[i+1] = Math.max(0, Math.min(255, gg + n + edge));
      out.data[i+2] = Math.max(0, Math.min(255, b  + n + edge));
      out.data[i+3] = 255;
    }
    g.putImageData(out,0,0); terrainImg = off; draw();
  };
  img.src = "data:image/png;base64," + meta.terrain_png;
}

/* Roads as drawn lines with a casing, the way a map sheet shows them, rather
   than as one-cell stripes in a raster. */
function drawRoads(g){
  const legs = [
    [meta.junction, meta.routes.west[0]],
    [meta.junction, meta.routes.east[0]],
    meta.routes.west, meta.routes.east,
  ];
  for (const pass of [0,1]){
    g.strokeStyle = pass ? "#6E5C3C" : "#151A1F";
    g.lineWidth = pass ? 2.4 : 4.6;
    g.lineCap = "round"; g.lineJoin = "round";
    for (const leg of legs){
      g.beginPath();
      leg.forEach((p,i) => { const [x,y] = P(p); i ? g.lineTo(x,y) : g.moveTo(x,y); });
      g.stroke();
    }
  }
}

/* A kilometre grid with edge labels: the reference has one, and without it the
   map gives the eye nothing to measure against. */
function drawGrid(g){
  const b = box();
  g.save();
  g.strokeStyle = "rgba(133,147,162,.16)"; g.lineWidth = 1;
  g.fillStyle = "rgba(133,147,162,.55)"; g.font = "9.5px ui-monospace,monospace";
  for (let km=0; km*1000 <= meta.width_m; km++){
    const [x] = P([km*1000, 0]), [, y] = P([0, km*1000]);
    g.beginPath(); g.moveTo(x, b.oy); g.lineTo(x, b.oy+b.side); g.stroke();
    g.beginPath(); g.moveTo(b.ox, y); g.lineTo(b.ox+b.side, y); g.stroke();
    if (km % 2 === 0){
      g.fillText(String(km*10).padStart(2,"0"), x+2, b.oy+11);
      g.fillText(String(km*10).padStart(2,"0"), b.ox+2, y-2);
    }
  }
  g.restore();
}

/* APP-6 style: friendly is a rectangle, hostile a diamond. */
function symbol(g, e){
  const [x,y] = P(e.pos);
  const s = 9, col = SIDE[e.side] || SIDE.neutral;
  const dead = e.status === "destroyed";
  g.save();
  g.globalAlpha = dead ? 0.4 : 1;
  g.lineWidth = 1.6; g.strokeStyle = col;
  g.fillStyle = e.side === "blue" ? "rgba(91,155,213,.22)" : "rgba(224,90,71,.22)";
  g.beginPath();
  if (e.side === "blue"){ g.rect(x-s*1.35, y-s*0.85, s*2.7, s*1.7); }
  else { g.moveTo(x, y-s); g.lineTo(x+s, y); g.lineTo(x, y+s); g.lineTo(x-s, y); g.closePath(); }
  g.fill(); g.stroke();

  // Role marks inside the frame, as a symbol set does.
  g.beginPath();
  if (e.kind === "infantry_platoon"){
    g.moveTo(x-s*1.1, y-s*0.7); g.lineTo(x+s*1.1, y+s*0.7);
    g.moveTo(x+s*1.1, y-s*0.7); g.lineTo(x-s*1.1, y+s*0.7);
  } else if (e.kind === "mech_company"){
    g.ellipse(x, y, s*0.85, s*0.5, 0, 0, 7);
  } else if (e.kind === "recon_troop"){
    g.moveTo(x-s*0.9, y+s*0.6); g.lineTo(x+s*0.9, y-s*0.6);
  } else if (e.kind === "drone"){
    g.moveTo(x-s*0.9, y); g.lineTo(x+s*0.9, y); g.moveTo(x, y-s*0.5); g.lineTo(x, y+s*0.5);
  }
  g.stroke();

  if (dead){ g.strokeStyle = "#E05A47"; g.lineWidth = 2; g.beginPath();
    g.moveTo(x-s*1.5,y-s*1.5); g.lineTo(x+s*1.5,y+s*1.5);
    g.moveTo(x+s*1.5,y-s*1.5); g.lineTo(x-s*1.5,y+s*1.5); g.stroke(); }

  // Strength bar under the symbol.
  if (!dead){
    const w = s*2.7;
    g.fillStyle = "rgba(0,0,0,.5)"; g.fillRect(x-w/2, y+s*1.25, w, 3);
    g.fillStyle = e.strength > .6 ? "#5FB878" : e.strength > .35 ? "#E0A84A" : "#E05A47";
    g.fillRect(x-w/2, y+s*1.25, w*e.strength, 3);
  }

  const dy = labelSlot(x + s*1.7, y - s*0.4);
  g.fillStyle = col; g.font = "600 10.5px ui-monospace,monospace";
  g.fillText(e.id, x + s*1.7, y - s*0.4 + dy);
  if (e.speed > 0.1){
    g.fillStyle = "#8593A2"; g.font = "10px ui-monospace,monospace";
    g.fillText(`${Math.round(e.heading)}° ${(e.speed*3.6).toFixed(0)} km/h`,
               x + s*1.7, y + s*0.9 + dy);
  }
  if (selected === e.id){
    g.strokeStyle = "#E0A84A"; g.lineWidth = 1.4; g.setLineDash([3,3]);
    g.beginPath(); g.arc(x, y, s*2.1, 0, 7); g.stroke(); g.setLineDash([]);
  }
  g.restore();
}

/* Labels in a cluster overwrite each other. Stack them instead. */
let labelsThisFrame = [];
function labelSlot(x, y){
  let dy = 0;
  for (let guard = 0; guard < 8; guard++){
    if (!labelsThisFrame.some(l => Math.abs(l.x - x) < 90 && Math.abs(l.y - (y+dy)) < 13)) break;
    dy += 15;
  }
  labelsThisFrame.push({x, y: y + dy});
  return dy;
}

function draw(){
  if (!meta) return;
  labelsThisFrame = [];
  const b = box();
  ctx.clearRect(0,0,cv.width,cv.height);
  if (terrainImg){ ctx.imageSmoothingEnabled = true;
    ctx.drawImage(terrainImg, b.ox, b.oy, b.side, b.side); }
  drawGrid(ctx);
  drawRoads(ctx);
  // The objective, so the white cell can see what the situation is about.
  const [ox,oy] = P(meta.objective);
  ctx.strokeStyle = "#E0A84A"; ctx.lineWidth = 1.6; ctx.setLineDash([4,3]);
  ctx.strokeRect(ox-14, oy-10, 28, 20); ctx.setLineDash([]);
  ctx.fillStyle = "#E0A84A"; ctx.font = "600 10.5px ui-monospace,monospace";
  ctx.fillText("KELO", ox-14, oy-14);
  if (!truth) return;

  // Reach rings first, so symbols sit on top.
  for (const e of truth.entities){
    if (e.status === "destroyed") continue;
    const [x,y] = P(e.pos);
    if ($("cSensor").checked && e.sensor_range_m > 0){
      ctx.strokeStyle = "rgba(95,184,120,.30)"; ctx.lineWidth = 1; ctx.setLineDash([4,5]);
      ctx.beginPath(); ctx.arc(x, y, M(e.sensor_range_m), 0, 7); ctx.stroke(); ctx.setLineDash([]);
    }
    if ($("cWeapon").checked && e.weapon_range_m > 0){
      ctx.strokeStyle = e.side === "red" ? "rgba(224,90,71,.35)" : "rgba(91,155,213,.30)";
      ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(x, y, M(e.weapon_range_m), 0, 7); ctx.stroke();
    }
  }

  // Plotted courses.
  if ($("cRoute").checked){
    for (const e of truth.entities){
      if (e.status === "destroyed" || !e.waypoint) continue;
      const legs = [e.pos, e.waypoint].concat(e.route);
      ctx.strokeStyle = e.side === "red" ? "rgba(224,90,71,.5)" : "rgba(91,155,213,.5)";
      ctx.lineWidth = 1.2; ctx.setLineDash([7,5]); ctx.beginPath();
      legs.forEach((p,i) => { const [x,y] = P(p); i ? ctx.lineTo(x,y) : ctx.moveTo(x,y); });
      ctx.stroke(); ctx.setLineDash([]);
      const [wx,wy] = P(e.waypoint);
      ctx.strokeRect(wx-3, wy-3, 6, 6);
    }
  }

  // Blue's believed picture: where blue thinks red is, and how stale that is.
  if ($("cBelief").checked){
    for (const b2 of truth.believed){
      if (!b2.subject.startsWith("red")) continue;
      const [x,y] = P(b2.pos);
      const fade = Math.max(0.2, 1 - b2.age_s/1800);
      ctx.strokeStyle = `rgba(224,168,74,${0.55*fade})`;
      ctx.setLineDash([2,3]); ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(x, y, Math.max(4, M(b2.uncertainty_m)), 0, 7); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = `rgba(224,168,74,${fade})`; ctx.font = "10px ui-monospace,monospace";
      const bdy = labelSlot(x + 6, y - 6);
      ctx.fillText(`blue believes · ${Math.round(b2.age_s/60)} min`, x + 6, y - 6 + bdy);
    }
  }

  // Fire lines for this tick.
  for (const g2 of truth.engagements){
    const a = truth.entities.find(e => e.id === g2.shooter);
    const t2 = truth.entities.find(e => e.id === g2.target);
    if (!a || !t2) continue;
    const [x1,y1] = P(a.pos), [x2,y2] = P(t2.pos);
    ctx.strokeStyle = a.side === "red" ? "rgba(224,90,71,.85)" : "rgba(232,237,243,.75)";
    ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    ctx.fillStyle = "#E0A84A";
    ctx.beginPath(); ctx.arc(x2, y2, 3.5, 0, 7); ctx.fill();
  }

  for (const e of truth.entities) symbol(ctx, e);

  // Scale bar, in metres, as the reference does.
  const km = 1000, w = M(km);
  ctx.fillStyle = "rgba(232,237,243,.75)"; ctx.font = "10px ui-monospace,monospace";
  ctx.fillRect(b.ox+14, b.oy+b.side-24, w, 3);
  ctx.fillText("0", b.ox+12, b.oy+b.side-30);
  ctx.fillText("1000 m", b.ox+14+w-30, b.oy+b.side-30);
}

/* ------------------------------------------------------------------ side --- */

function renderUnits(){
  $("units").innerHTML = truth.entities.map(e => {
    const dead = e.status === "destroyed";
    const col = e.strength > .6 ? "#5FB878" : e.strength > .35 ? "#E0A84A" : "#E05A47";
    return `<div class="unit ${selected===e.id?"sel":""} ${dead?"dead":""}" data-id="${e.id}">
      <span class="name" style="color:${SIDE[e.side]}">${e.id}</span>
      <span style="color:#8593A2">${dead?"destroyed":e.status}</span>
      <span class="meta">${e.kind} · ${(e.strength*100).toFixed(0)} % · ${
        e.speed>0.1?`${Math.round(e.heading)}° ${(e.speed*3.6).toFixed(0)} km/h`:"halted"}${
        e.endurance_s!==null&&e.endurance_s!==undefined?` · endurance ${Math.round(e.endurance_s/60)} min`:""}</span>
      <span class="bar"><i style="width:${e.strength*100}%;background:${col}"></i></span>
    </div>`;
  }).join("");
}

function renderLog(){
  $("log").innerHTML = truth.log_tail.slice().reverse().map(r => {
    let text = "";
    if (r.type === "engagement") text = `${r.shooter} → ${r.target} at ${Math.round(r.range_m)} m`;
    else if (r.type === "unit_destroyed") text = `${r.entity} destroyed`;
    else if (r.type === "radio_message") text = `${r.sender}: ${r.text}`;
    else if (r.type === "weather_change") text = `met: ${r.label}`;
    else if (r.type === "query") text = `participant asks: ${r.raw_text}`;
    else if (r.type === "answer") text = `channel: ${r.intent}${r.injection?" · INJECTED "+r.injection:""}`;
    else if (r.type === "decision") text = `decision: ${r.action}`;
    else if (r.type === "freeze_start") text = `freeze — display blanked`;
    else if (r.type === "probe_shown") text = `probe ${r.ref}`;
    return `<div class="${r.type}"><span class="t">${fmt(r.t_scen)}</span>${text}</div>`;
  }).join("");
}

function apply(v){
  truth = v;
  $("clock").textContent = fmt(v.t);
  $("remain").textContent = `· ${Math.max(0,Math.round((v.duration_s-v.t)/60))} min to go`
                            + (v.freeze ? " · FREEZE" : "");
  $("met").textContent = v.weather.label + ` · vis ${(v.weather.visibility_m/1000).toFixed(1)} km`;
  renderUnits(); renderLog(); draw();
}

/* ------------------------------------------------------------------ loop --- */

function setRate(x){
  rate = x;
  document.querySelectorAll("#speed button").forEach(b =>
    b.setAttribute("aria-pressed", String(Number(b.dataset.x) === x)));
  if (timer) clearInterval(timer);
  if (x > 0) timer = setInterval(() => {
    post("/api/tick_n", {n:x, truth:true}).then(v => {
      apply(v);
      if (REPLAY && frame >= REPLAY.frames.length - 1) setRate(0);
    });
  }, 1000);
}

$("speed").onclick = e => { const b = e.target.closest("button"); if (b) setRate(Number(b.dataset.x)); };
$("units").onclick = e => { const u = e.target.closest(".unit"); if (!u) return;
  selected = selected === u.dataset.id ? null : u.dataset.id; renderUnits(); draw(); };
["cWeapon","cSensor","cBelief","cRoute"].forEach(id => $(id).onchange = draw);

$("stage").addEventListener("mousemove", ev => {
  if (!meta) return;
  const r = cv.getBoundingClientRect(), b = box();
  const mx = ((ev.clientX - r.left) - b.ox) / b.side * meta.width_m;
  const my = ((ev.clientY - r.top) - b.oy) / b.side * meta.width_m;
  if (mx < 0 || my < 0 || mx > meta.width_m || my > meta.width_m){ $("rCoord").textContent = "—"; return; }
  $("rCoord").textContent = `grid ${Math.floor(mx/100).toString().padStart(2,"0")}-${Math.floor(my/100).toString().padStart(2,"0")}`;
  $("rTerrain").textContent = `${(mx/1000).toFixed(2)} km E · ${(my/1000).toFixed(2)} km S`;
});

(async () => {
  meta = REPLAY ? REPLAY.meta
                : await (await fetch(`/api/scenario/${SCENARIO}`)).json();
  paintTerrain(); fit();
  if (REPLAY){
    apply(REPLAY.frames[0]);
  } else {
    await post("/api/start", {scenario: SCENARIO});
    apply(await post("/api/truth", {}));
  }
  $("rScale").textContent = `${(meta.width_m/1000).toFixed(0)} × ${(meta.width_m/1000).toFixed(0)} km`;
  setRate(5);
})();
