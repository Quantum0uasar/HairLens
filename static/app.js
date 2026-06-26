const $ = (id) => document.getElementById(id);
const fileInput = $("file");
const dropzone = $("dropzone");
const dzInner = $("dzInner");
const preview = $("preview");
const analyzeBtn = $("analyzeBtn");
const hint = $("hint");

let selectedFile = null;
let lastCuts = null;

function setFile(file) {
  if (!file || !file.type.startsWith("image/")) {
    hint.textContent = "That doesn't look like an image. Try a JPG or PNG.";
    return;
  }
  selectedFile = file;
  hint.textContent = "";
  const url = URL.createObjectURL(file);
  preview.src = url;
  preview.hidden = false;
  dzInner.hidden = true;
  analyzeBtn.disabled = false;
}

fileInput.addEventListener("change", (e) => setFile(e.target.files[0]));

["dragenter", "dragover"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag");
  })
);
["dragleave", "drop"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag");
  })
);
dropzone.addEventListener("drop", (e) => setFile(e.dataTransfer.files[0]));
dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") fileInput.click();
});

analyzeBtn.addEventListener("click", analyze);

async function analyze() {
  if (!selectedFile) return;
  analyzeBtn.classList.add("loading");
  analyzeBtn.disabled = true;
  hint.textContent = "";

  try {
    const form = new FormData();
    form.append("file", selectedFile);
    const res = await fetch("/analyze", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || "Analysis failed.");
    render(data);
  } catch (err) {
    hint.textContent = err.message || "Something went wrong. Try again.";
  } finally {
    analyzeBtn.classList.remove("loading");
    analyzeBtn.disabled = false;
  }
}

function barColor(key, val) {
  const good = key === "hydration_score" || key === "shine_score";
  if (good) return val >= 50 ? "var(--teal)" : "var(--amber)";
  return val >= 50 ? "var(--rose)" : "var(--teal)";
}

const SCORE_LABELS = {
  hydration_score: "Hydration",
  damage_score: "Damage",
  frizz_score: "Frizz",
  shine_score: "Shine",
};

function render(data) {
  const a = data.analysis || {};
  const report = $("report");

  $("reportImg").src = preview.src;
  $("observation").textContent = a.observations ? `“${a.observations}”` : "";

  const conf = $("confidence");
  conf.textContent = (a.confidence || "low") + " confidence";

  if (!a.hair_visible) {
    $("traits").innerHTML =
      `<div><dt>Result</dt><dd>Hair not clearly visible</dd></div>`;
    $("bars").innerHTML = `<p class="why">${a.confidence_note || "Try a closer, well-lit photo of your hair."}</p>`;
    $("cards").innerHTML = "";
    $("cutsSection").hidden = true;
    report.hidden = false;
    report.scrollIntoView({ behavior: "smooth" });
    return;
  }

  const traitFields = [
    ["Hair type", a.hair_type],
    ["Texture", a.texture],
    ["Hydration", a.hydration_level],
    ["Condition", a.hair_condition],
    ["Porosity", a.porosity],
  ];
  $("traits").innerHTML = traitFields
    .map(([k, v]) => `<div><dt>${k}</dt><dd>${v || "—"}</dd></div>`)
    .join("");

  const scores = a.scores || {};
  $("bars").innerHTML = Object.keys(SCORE_LABELS)
    .map((key) => {
      const v = scores[key] ?? 50;
      return `<div class="bar">
        <div class="bar-top"><span>${SCORE_LABELS[key]}</span><span class="bar-num">${v}</span></div>
        <div class="bar-track"><div class="bar-fill" data-w="${v}" style="background:${barColor(key, v)}"></div></div>
      </div>`;
    })
    .join("");
  requestAnimationFrame(() => {
    document.querySelectorAll(".bar-fill").forEach((el) => {
      el.style.width = el.dataset.w + "%";
    });
  });

  const hc = (data.recommendations && data.recommendations.haircare) || {};
  const order = [
    ["shampoo", "Shampoo"],
    ["conditioner", "Conditioner"],
    ["treatment", "Treatment"],
    ["scalp", "Scalp / growth"],
  ];
  $("cards").innerHTML = order
    .filter(([slot]) => hc[slot])
    .map(([slot, label]) => {
      const p = hc[slot];
      return `<div class="pcard">
        <span class="slot">${label}</span>
        <span class="pname">${p.name}</span>
        <span class="price">${p.price || ""}</span>
        <span class="why">${p.helps || p.why || ""}</span>
        <span class="when"><strong>When:</strong> ${p.when || ""}</span>
        <a href="${p.link}" target="_blank" rel="noopener">Find it →</a>
      </div>`;
    })
    .join("");

  const cuts = data.haircuts || {};
  const cutsSection = $("cutsSection");
  if (cuts.options && (cuts.options.women || cuts.options.men)) {
    lastCuts = cuts;
    $("cutsShape").textContent = "· " + cuts.face_shape + " face";
    $("cutsSummary").textContent = cuts.summary || "";
    $("cutsAvoid").textContent = cuts.avoid ? "Skip: " + cuts.avoid : "";
    setupToggle(cuts.default_tab || "women");
    cutsSection.hidden = false;
  } else {
    cutsSection.hidden = true;
  }

  report.hidden = false;
  report.scrollIntoView({ behavior: "smooth" });
}

function setupToggle(activeTab) {
  const btns = document.querySelectorAll(".tog-btn");
  btns.forEach((b) => {
    b.classList.toggle("active", b.dataset.tab === activeTab);
    b.onclick = () => {
      btns.forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      renderCuts(b.dataset.tab);
    };
  });
  renderCuts(activeTab);
}

function renderCuts(tab) {
  if (!lastCuts) return;
  const list = (lastCuts.options && lastCuts.options[tab]) || [];
  $("cutCards").innerHTML = list
    .map((s, i) => `<div class="pcard">
      <span class="slot">Cut</span>
      <span class="pname">${s.name}</span>
      <span class="why">${s.why || ""}</span>
      <button class="preview-btn" data-cut="${s.name.replace(/"/g, "&quot;")}" data-i="${i}">Preview on me</button>
      <div class="preview-slot" id="preview-${i}"></div>
    </div>`)
    .join("");
  document.querySelectorAll(".preview-btn").forEach((btn) => {
    btn.addEventListener("click", () => previewCut(btn));
  });
}

async function previewCut(btn) {
  if (!selectedFile) return;
  const cut = btn.dataset.cut;
  const slot = document.getElementById("preview-" + btn.dataset.i);
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "Generating…";
  slot.innerHTML = '<p class="preview-note">Rendering your AI preview… (10–20s)</p>';

  try {
    const form = new FormData();
    form.append("file", selectedFile);
    form.append("cut", cut);
    const res = await fetch("/preview", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || "Preview failed.");
    slot.innerHTML =
      `<img class="preview-img" src="${data.image}" alt="AI preview of ${cut}" />
       <p class="preview-note">AI visualization — approximate, not a real photo.</p>`;
    btn.textContent = "Regenerate";
  } catch (err) {
    slot.innerHTML = `<p class="preview-err">${err.message}</p>`;
    btn.textContent = original;
  } finally {
    btn.disabled = false;
  }
}
