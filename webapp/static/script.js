const COLS = 3, ROWS = 3;
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
const CELL = canvas.width / COLS;

const levelSelect = document.getElementById("level-select");
const solveBtn = document.getElementById("solve-btn");
const statsEl = document.getElementById("stats");
const playBtn = document.getElementById("play-btn");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const resetBtn = document.getElementById("reset-btn");
const speedInput = document.getElementById("speed");
const stepLabel = document.getElementById("step-label");
const stepSlider = document.getElementById("step-slider");
const moveLog = document.getElementById("move-log");

let solution = null;     // full /api/solve response
let frames = [];         // list of board-state snapshots, one per step (0 = initial)
let stepIdx = 0;
let playing = false;
let playTimer = null;
const tileImages = {};

function loadTileImages() {
  const letters = ["A", "B", "C", "D", "E", "F", "G", "H"];
  return Promise.all(letters.map(letter => new Promise(resolve => {
    const img = new Image();
    img.onload = () => { tileImages[letter] = img; resolve(); };
    img.onerror = () => resolve(); // tolerate missing asset, fall back to block color
    img.src = `assets/tile_${letter}.png`;
  })));
}

async function fetchLevels() {
  const res = await fetch("/api/levels");
  const levels = await res.json();
  levelSelect.innerHTML = "";
  for (const lvl of levels) {
    const opt = document.createElement("option");
    opt.value = lvl;
    opt.textContent = lvl;
    levelSelect.appendChild(opt);
  }
}

async function solveCurrentLevel() {
  stopPlayback();
  solveBtn.disabled = true;
  statsEl.textContent = "Solving...";
  const level = levelSelect.value;
  const res = await fetch(`/api/solve/${encodeURIComponent(level)}`);
  solution = await res.json();
  solveBtn.disabled = false;

  if (!solution.solved) {
    statsEl.innerHTML = `<strong>No solution found</strong> within search limits.`;
    frames = [];
    drawEmpty();
    return;
  }

  statsEl.innerHTML =
    `<strong>${solution.total_cost}</strong> total cost &middot; ` +
    `${solution.steps.length} steps<br>` +
    `${solution.nodes_expanded} A* nodes expanded &middot; ` +
    `${solution.solve_time_ms} ms`;

  buildFrames();
  buildMoveLog();
  stepIdx = 0;
  stepSlider.max = frames.length - 1;
  stepSlider.value = 0;
  renderFrame(0);
}

function buildFrames() {
  // frame 0 = initial board; frame i = board state after step i
  const tiles = solution.board.slice();
  const orientation = solution.orientation.slice();
  let pawn = solution.pawn_pos;
  let layer = "Ground";

  frames = [{ tiles: tiles.slice(), orientation: orientation.slice(), pawn, layer, stepTaken: null }];

  for (const step of solution.steps) {
    if (step.action === "slide") {
      const blankIdx = tiles.indexOf(" ");
      [tiles[blankIdx], tiles[step.tile_idx]] = [tiles[step.tile_idx], tiles[blankIdx]];
      [orientation[blankIdx], orientation[step.tile_idx]] = [orientation[step.tile_idx], orientation[blankIdx]];
    } else {
      pawn = step.dest_idx;
      layer = step.dest_layer;
    }
    frames.push({ tiles: tiles.slice(), orientation: orientation.slice(), pawn, layer, stepTaken: step });
  }
}

function buildMoveLog() {
  moveLog.innerHTML = "";
  solution.steps.forEach((step, i) => {
    const li = document.createElement("li");
    li.dataset.step = i + 1;
    if (step.action === "slide") {
      li.textContent = `Slide tile at cell ${step.tile_idx} (cost 1)`;
    } else {
      li.textContent = `Walk pawn to cell ${step.dest_idx} on ${step.dest_layer} (cost ${step.cost})`;
    }
    moveLog.appendChild(li);
  });
}

function highlightLog(idx) {
  [...moveLog.children].forEach((li, i) => {
    li.classList.toggle("active", i === idx - 1);
  });
  if (idx > 0 && moveLog.children[idx - 1]) {
    moveLog.children[idx - 1].scrollIntoView({ block: "nearest" });
  }
}

function drawEmpty() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#2a241c";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function renderFrame(idx) {
  if (!frames.length) return;
  stepIdx = Math.max(0, Math.min(idx, frames.length - 1));
  const frame = frames[stepIdx];

  drawEmpty();

  for (let i = 0; i < 9; i++) {
    const symbol = frame.tiles[i];
    if (symbol === " ") continue;
    const letter = solution.symbol_to_letter[symbol];
    const r = Math.floor(i / COLS), c = i % COLS;
    const x = c * CELL, y = r * CELL;
    const rotDeg = -frame.orientation[i] * 90;

    ctx.save();
    ctx.translate(x + CELL / 2, y + CELL / 2);
    ctx.rotate((rotDeg * Math.PI) / 180);

    const img = letter ? tileImages[letter] : null;
    if (img && img.complete && img.naturalWidth) {
      ctx.drawImage(img, -CELL / 2, -CELL / 2, CELL, CELL);
    } else {
      ctx.fillStyle = "#3a2f23";
      ctx.fillRect(-CELL / 2, -CELL / 2, CELL, CELL);
      ctx.strokeStyle = "#000";
      ctx.strokeRect(-CELL / 2, -CELL / 2, CELL, CELL);
    }
    ctx.restore();
  }

  // pawn
  const pr = Math.floor(frame.pawn / COLS), pc = frame.pawn % COLS;
  const px = pc * CELL + CELL / 2, py = pr * CELL + CELL / 2;
  ctx.beginPath();
  ctx.arc(px, py, CELL * 0.14, 0, Math.PI * 2);
  ctx.fillStyle = frame.layer === "Ground" ? "#e2503f" : "#f2c245";
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#fff";
  ctx.stroke();

  stepLabel.textContent = `Step ${stepIdx} / ${frames.length - 1}`;
  stepSlider.value = stepIdx;
  highlightLog(stepIdx);

  const atEnd = stepIdx >= frames.length - 1;
  if (atEnd) stopPlayback();
}

function stepForward() { renderFrame(stepIdx + 1); }
function stepBackward() { renderFrame(stepIdx - 1); }

function stopPlayback() {
  playing = false;
  playBtn.textContent = "▶";
  if (playTimer) clearTimeout(playTimer);
  playTimer = null;
}

function startPlayback() {
  if (!frames.length || stepIdx >= frames.length - 1) return;
  playing = true;
  playBtn.textContent = "⏸";
  const tick = () => {
    if (!playing) return;
    if (stepIdx >= frames.length - 1) { stopPlayback(); return; }
    stepForward();
    playTimer = setTimeout(tick, Number(speedInput.value));
  };
  playTimer = setTimeout(tick, Number(speedInput.value));
}

playBtn.addEventListener("click", () => (playing ? stopPlayback() : startPlayback()));
prevBtn.addEventListener("click", () => { stopPlayback(); stepBackward(); });
nextBtn.addEventListener("click", () => { stopPlayback(); stepForward(); });
resetBtn.addEventListener("click", () => { stopPlayback(); renderFrame(0); });
stepSlider.addEventListener("input", () => { stopPlayback(); renderFrame(Number(stepSlider.value)); });
solveBtn.addEventListener("click", solveCurrentLevel);

document.addEventListener("keydown", (e) => {
  if (e.code === "Space") { e.preventDefault(); playing ? stopPlayback() : startPlayback(); }
  if (e.code === "ArrowRight") { stopPlayback(); stepForward(); }
  if (e.code === "ArrowLeft") { stopPlayback(); stepBackward(); }
});

(async function init() {
  await loadTileImages();
  await fetchLevels();
  drawEmpty();
  await solveCurrentLevel();
})();
