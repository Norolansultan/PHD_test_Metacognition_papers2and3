"use strict";
/* Participant display.
   Two rules this file exists to keep:
     1. It draws from the belief layer the server sends. It never receives world
        truth, so it cannot render it (ADR-001).
     2. During a freeze the display is blanked and the channel refuses to answer.
        Nothing anywhere anticipates a freeze or a probe.                        */

const params = new URLSearchParams(location.search);
const PID = params.get("pid") || "p001";
const SCENARIO = params.get("scenario") || "fin-def-03";
const CONDITION = params.get("condition") || "ai_mediated";

const $ = id => document.getElementById(id);
const cv = $("map"), ctx = cv.getContext("2d");
const COLOUR = {open:"#2A3138", forest:"#263A2C", water:"#1E3A4C", road:"#5A4A2E",
                urban:"#3A3630", track:"#3E3823"};
let meta = null, terrain = null, view = null, timer = null, probeState = {};

async function post(path, body){
  const r = await fetch(path, {method:"POST", headers:{"Content-Type":"application/json"},
                              body: JSON.stringify(Object.assign({pid:PID}, body||{}))});
  return r.json();
}

function fmt(s){ return `${Math.floor(s/60)}:${String(s%60).padStart(2,"0")}`; }
function px(m){ return (m / meta.width_m) * cv.width; }

function paintTerrain(){
  const img = new Image();
  img.onload = () => {
    const off = document.createElement("canvas");
    off.width = img.width; off.height = img.height;
    const g = off.getContext("2d");
    g.drawImage(img,0,0);
    const d = g.getImageData(0,0,img.width,img.height);
    for (let i=0;i<d.data.length;i+=4){
      const c = COLOUR[meta.legend[String(d.data[i])]] || COLOUR.open;
      d.data[i]=parseInt(c.slice(1,3),16); d.data[i+1]=parseInt(c.slice(3,5),16);
      d.data[i+2]=parseInt(c.slice(5,7),16); d.data[i+3]=255;
    }
    g.putImageData(d,0,0);
    terrain = off; draw();
  };
  img.src = "data:image/png;base64," + meta.terrain_png;
}

function draw(){
  ctx.clearRect(0,0,cv.width,cv.height);
  if (terrain){ ctx.imageSmoothingEnabled = false; ctx.drawImage(terrain,0,0,cv.width,cv.height); }
  if (!view) return;

  /* Believed contacts: position, age, and an uncertainty that grows on its own. */
  for (const b of view.beliefs){
    const fade = Math.max(0.2, 1 - b.age_s/1800);
    ctx.save();
    ctx.strokeStyle = `rgba(255,123,92,${0.6*fade})`;
    ctx.fillStyle   = `rgba(255,123,92,${0.10*fade})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(px(b.pos[0]), px(b.pos[1]), Math.max(5, px(b.uncertainty_m)), 0, 7);
    ctx.fill(); ctx.stroke();
    ctx.fillStyle = `rgba(255,123,92,${fade})`;
    ctx.beginPath(); ctx.arc(px(b.pos[0]), px(b.pos[1]), 5, 0, 7); ctx.fill();
    ctx.font = "600 12px ui-monospace,monospace";
    ctx.fillText(`${b.subject} · ${Math.round(b.age_s/60)} min`, px(b.pos[0])+9, px(b.pos[1])-9);
    ctx.restore();
  }

  for (const [id,u] of Object.entries(view.own)){
    const drone = id.includes("drone");
    ctx.fillStyle = drone ? "#7FB2DC" : "#B7D3EA";
    if (drone){ ctx.beginPath(); ctx.arc(px(u.pos[0]), px(u.pos[1]), 5, 0, 7); ctx.fill(); }
    else ctx.fillRect(px(u.pos[0])-6, px(u.pos[1])-6, 12, 12);
    ctx.fillStyle = "#B7D3EA"; ctx.font = "600 11px ui-monospace,monospace";
    ctx.fillText(id, px(u.pos[0])+10, px(u.pos[1])+4);
  }
}

function renderUnits(){
  $("units").innerHTML = Object.entries(view.own).map(([id,u]) => {
    const air = u.endurance_s !== null && u.endurance_s !== undefined;
    const extra = air ? ` · endurance ${Math.round(u.endurance_s/60)} min` : "";
    return `${id} — ${u.status}${extra}`;
  }).join("<br>");
}

function renderRadio(msgs){
  if (!msgs.length) return;
  const box = $("msgs");
  for (const m of msgs){
    const el = document.createElement("div");
    el.className = "msg";
    el.innerHTML = `<span class="who">${fmt(m.t)} ${m.sender}</span><br>${m.text}`;
    box.appendChild(el);
  }
  $("radio").scrollTop = $("radio").scrollHeight;
}

/* ---------------------------------------------------------------- freeze --- */

function showFreeze(f){
  probeState = {choice:null, confidence:null, isa:null};
  const box = $("freezebox");
  const opts = f.open_l3
    ? `<textarea id="ptext" placeholder="in your own words"></textarea>`
    : ["A: still east of the lake","B: on the northern lateral",
       "C: west of the lake, closing on KELO","D: no basis to judge"]
      .map((o,i) => `<button class="opt" data-opt="${"ABCD"[i]}">${o}</button>`).join("");
  box.innerHTML = `
    <h1>${f.open_l3 ? "What do you expect to happen in the next 30 minutes, and why?"
                    : "Where do you estimate the enemy detachment will be in 30 minutes?"}</h1>
    ${opts}
    <div class="lbl">How confident are you in that answer?</div>
    <div class="scale" id="conf">${[1,2,3,4].map(n =>
      `<button data-conf="${n}">${n}</button>`).join("")}</div>
    <div class="lbl">Current workload</div>
    <div class="scale" id="isa">${[1,2,3,4,5].map(n =>
      `<button data-isa="${n}">${n}</button>`).join("")}</div>
    <button class="primary" id="psubmit" style="margin-top:18px" disabled>Continue</button>`;
  $("freeze").style.display = "flex";

  box.onclick = async ev => {
    const b = ev.target.closest("button"); if (!b) return;
    if (b.dataset.opt){ probeState.choice = b.dataset.opt;
      box.querySelectorAll("[data-opt]").forEach(x => x.classList.remove("sel"));
      b.classList.add("sel"); }
    if (b.dataset.conf){ probeState.confidence = Number(b.dataset.conf);
      box.querySelectorAll("[data-conf]").forEach(x => x.classList.remove("sel"));
      b.classList.add("sel"); }
    if (b.dataset.isa){ probeState.isa = Number(b.dataset.isa);
      box.querySelectorAll("[data-isa]").forEach(x => x.classList.remove("sel"));
      b.classList.add("sel"); }
    const text = $("ptext") ? $("ptext").value.trim() : null;
    const answered = f.open_l3 ? true : probeState.choice !== null;
    $("psubmit").disabled = !(answered && probeState.confidence && probeState.isa);
    if (b.id === "psubmit"){
      await post("/api/probe", {choice: probeState.choice, text,
                                confidence: probeState.confidence});
      view = await post("/api/isa", {value: probeState.isa});
      $("freeze").style.display = "none";
      draw();
    }
  };
}

/* ------------------------------------------------------------------ loop --- */

async function loop(){
  view = await post("/api/tick", {scenario: SCENARIO});
  $("clock").textContent = fmt(view.t);
  renderRadio(view.radio);
  renderUnits();
  draw();
  if (view.freeze) showFreeze(view.freeze);
  if (view.finished){ clearInterval(timer); $("clock").textContent += " — ended"; }
}

async function ask(){
  const text = $("q").value.trim();
  if (!text) return;
  $("q").value = "";
  $("answer").className = "waiting";
  $("answer").textContent = "…";
  const t0 = performance.now();
  const r = await post("/api/ask", {text});
  $("answer").className = "";
  $("answer").textContent = r.answer.text;
  view = r.view; draw();
  console.log(`answer in ${Math.round(performance.now()-t0)} ms`);
}

async function begin(){
  if (innerWidth < 1000 || innerHeight < 640){ $("toosmall").style.display = "flex"; return; }
  try { await document.documentElement.requestFullscreen(); } catch (e) { /* recorded below */ }
  $("gate").style.display = "none";
  $("app").style.display = "grid";
  $("who").textContent = `${PID} · ${SCENARIO}`;
  meta = await (await fetch(`/api/scenario/${SCENARIO}`)).json();
  paintTerrain();
  view = await post("/api/start", {scenario: SCENARIO, condition: CONDITION});
  renderUnits(); draw();
  timer = setInterval(loop, 1000);   // one scenario tick per wall second
}

$("begin").onclick = begin;
$("q").addEventListener("keydown", e => { if (e.key === "Enter") ask(); });
$("finish").onclick = async () => {
  clearInterval(timer);
  const r = await post("/api/finish", {scenario: SCENARIO});
  alert(`Session recorded: ${r.events} events.`);
};
document.addEventListener("click", async e => {
  const b = e.target.closest("[data-move]"); if (!b) return;
  /* A corridor is a route, not a point: a straight line to the objective runs
     into the lake, which is exactly why the corridors exist. */
  const route = b.dataset.move === "west"
    ? [[2850,3050],[2850,7550],[4150,7550]]
    : [[7050,3050],[7050,7550],[4150,7550]];
  view = await post("/api/decide", {action: `move_${b.dataset.move}`, unit: "blue_1pl",
                                    route});
  draw();
});

/* Leaving full screen or the tab cannot be prevented. It is measured. */
document.addEventListener("visibilitychange", () => {
  if (document.hidden) post("/api/focus_lost", {reason: "tab_hidden"});
});
document.addEventListener("fullscreenchange", () => {
  if (!document.fullscreenElement) post("/api/focus_lost", {reason: "left_fullscreen"});
});
addEventListener("blur", () => post("/api/focus_lost", {reason: "window_blur"}));
