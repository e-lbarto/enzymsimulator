/**
 * ENZYM-SIMULATOR v3 Logic
 */

const canvas = document.getElementById('beakerCanvas');
const ctx = canvas.getContext('2d');
const graphCanvas = document.getElementById('graphCanvas');
const gctx = graphCanvas.getContext('2d');

// --- Dynamic Color Fetching ---
function getC(varName) {
    return getComputedStyle(document.body).getPropertyValue(varName).trim();
}

// --- Simulation Constants ---
const BASE_SPEED = 3.6;
const BASE_TEMP = 25.0; // Basis 25°C in v3
const DENATURE_NORMAL = 50;
const DENATURE_THERMO = 80;
let ENZYME_R = 25;
let SUBSTRATE_R = 8;
let COLL_DIST = ENZYME_R + SUBSTRATE_R + 8;

// --- State ---
let running = false;
let enzymes = [];
let substrates = [];
let products = [];
let reactionsDone = 0;
let winTime = 0.0;
let accumulatedTime = 0.0;
let lastTickTime = 0;
let initialSubstratesCount = 0;
let scale = 1.0;
let finishTimer = 0; // Timer for 1s cooldown after completion
let graphHitRegions = []; // For Km/Vmax tooltips

let config = {
    temp: 25,
    numEnzymes: 4,
    numSubstrates: 100,
    thermostable: false,
    simSpeed: 1.0,
    showCurve: false,
    showKm: false,
    zoom: false,
    hasSavedData: false,
    hasRecordedRate: false,
    recordedRate: 0.0,
    theme: 'dark' // dark or paper
};

let dataPoints = []; // [s_cnt, rate, n_enz, temp]

// --- Utils ---
function rgtFactor(temp) {
    return Math.pow(2.0, (temp - BASE_TEMP) / 10.0);
}

function mmRate(s, n_enz, temp, thermo) {
    const fac = rgtFactor(temp);
    const tMid = thermo ? DENATURE_THERMO : DENATURE_NORMAL;
    const tStart = tMid - 10;
    const tEnd = tMid + 10;
    let denatFrac = 0.0;
    
    // Smooth denaturation curve like python
    if (thermo) {
        if (temp >= 90) denatFrac = 1.0;
        else if (temp >= 70) denatFrac = (temp - 70) / 20.0;
    } else {
        if (temp >= 60) denatFrac = 1.0;
        else if (temp >= 40) denatFrac = 0.25 + 0.75 * ((temp - 40) / 20.0);
    }
    
    const activeEnz = n_enz * (1.0 - denatFrac);
    const vmax = activeEnz * 14.0 * fac;
    const km = 20.0;
    
    if (s <= 0) return 0.0;
    const effective_s = Math.min(s, 150.0);
    let v = vmax * effective_s / (km + effective_s);
    if (s > 190.0) {
        const drop = 0.25 * (1.0 - Math.exp(-(s - 190.0) / 60.0));
        v *= (1.0 - drop);
    }
    return v;
}

function updateCanvasSize() {
    canvas.width = 380 * scale;
    canvas.height = 395 * scale;
    // Keep it centered in the container via margin
    canvas.style.margin = "0 auto";
    canvas.style.display = "block";
}

// --- Particles ---
class Particle {
    constructor(x, y, vx, vy) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
    }
    move(factor, width, height, padding) {
        this.x += this.vx * factor;
        this.y += this.vy * factor;
        if (this.x < padding || this.x > width - padding) {
            this.vx *= -1;
            this.x = Math.max(padding, Math.min(width - padding, this.x));
        }
        if (this.y < padding || this.y > height - padding) {
            this.vy *= -1;
            this.y = Math.max(padding, Math.min(height - padding, this.y));
        }
    }
}

class Enzyme extends Particle {
    constructor(x, y) {
        const ang = Math.random() * Math.PI * 2;
        const spd = BASE_SPEED * 0.44 * scale;
        super(x, y, Math.cos(ang) * spd, Math.sin(ang) * spd);
        this.bindingTimer = 0;
        this.denatured = false;
        this.denatureThreshold = null;
        this.seed = Math.random();
    }
    
    checkDenaturation(remaining, temp, thermo) {
        if (this.denatured) return;
        if (this.denatureThreshold !== null && remaining <= this.denatureThreshold) {
            this.denatured = true;
        }
    }

    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        const r = ENZYME_R;
        
        if (this.denatured) {
            ctx.beginPath();
            ctx.fillStyle = getC('--enz-denat');
            ctx.strokeStyle = getC('--enz-d-outline');
            ctx.lineWidth = 1.5;
            for (let i = 0; i < 14; i++) {
                const t = (Math.PI * 2 * i) / 14;
                const dist = r * (0.8 + Math.sin(t * 3 + this.seed * 10) * 0.2);
                const px = Math.cos(t) * dist;
                const py = Math.sin(t) * dist * 0.6;
                if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill(); ctx.stroke();
            ctx.beginPath();
            ctx.strokeStyle = getC('--error-color');
            ctx.lineWidth = 2.5;
            const s = r * 0.38;
            ctx.moveTo(-s, -s); ctx.lineTo(s, s);
            ctx.moveTo(s, -s); ctx.lineTo(-s, s);
            ctx.stroke();
        } else {
            ctx.beginPath();
            ctx.fillStyle = this.bindingTimer > 0 ? getC('--enz-binding') : getC('--enz-active');
            ctx.strokeStyle = getC('--enz-outline');
            ctx.lineWidth = 1.5;
            for(let i=0; i<=5; i++) {
                const a = Math.PI - (Math.PI * 0.35) * (i/5);
                ctx.lineTo(r * Math.cos(a), r * 0.8 * -Math.sin(a));
            }
            ctx.lineTo(-r * 0.4, -r * 0.7);
            ctx.lineTo(-r * 0.25, -r * 0.2);
            ctx.lineTo(-r * 0.1, -r * 0.2);
            ctx.lineTo(-r * 0.05, -r * 0.5);
            ctx.lineTo(r * 0.05, -r * 0.5);
            ctx.lineTo(r * 0.1, -r * 0.2);
            ctx.lineTo(r * 0.25, -r * 0.2);
            ctx.lineTo(r * 0.4, -r * 0.7);
            for(let i=0; i<=5; i++) {
                const a = (Math.PI * 0.35) * (1 - i/5);
                ctx.lineTo(r * Math.cos(a), r * 0.8 * -Math.sin(a));
            }
            for(let i=1; i<=20; i++) {
                const a = -Math.PI * (i/20);
                ctx.lineTo(r * Math.cos(a), r * 0.8 * -Math.sin(a));
            }
            ctx.closePath();
            ctx.fill(); ctx.stroke();

            if (this.bindingTimer > 0) {
                drawSubstrateShape(ctx, 0, -r * 0.3, SUBSTRATE_R * 0.8, getC('--sub-color'));
            }
        }
        ctx.restore();
    }
}

class Substrate extends Particle {
    constructor(x, y) {
        const ang = Math.random() * Math.PI * 2;
        const spd = BASE_SPEED * (2.0 + Math.random() * 0.8) * scale;
        super(x, y, Math.cos(ang) * spd, Math.sin(ang) * spd);
        this.baseSpd = spd;
        this.reacted = false;
    }
    draw(ctx) {
        drawSubstrateShape(ctx, this.x, this.y, SUBSTRATE_R, getC('--sub-color'));
    }
    move(factor, width, height, enzymes, remaining, padding) {
        let target = null;
        let minDist = Infinity;
        for (let e of enzymes) {
            if (!e.denatured && e.bindingTimer <= 0) {
                const d = Math.hypot(e.x - this.x, e.y - this.y);
                if (d < minDist) { minDist = d; target = e; }
            }
        }
        if (target) {
            const dx = target.x - this.x;
            const dy = target.y - this.y;
            const dist = Math.max(minDist, 1.0);
            const pull = remaining < 10 ? 1.2 : 0.4;
            this.vx += (dx / dist) * pull;
            this.vy += (dy / dist) * pull;
            const curSpd = Math.hypot(this.vx, this.vy);
            if (curSpd > 0) {
                this.vx = (this.vx / curSpd) * this.baseSpd;
                this.vy = (this.vy / curSpd) * this.baseSpd;
            }
        }
        super.move(factor, width, height, padding);
    }
}

class Product extends Particle {
    constructor(x, y) {
        const ang = Math.random() * Math.PI * 2;
        const spd = BASE_SPEED * 0.36 * scale;
        super(x, y, Math.cos(ang) * spd, Math.sin(ang) * spd);
    }
    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.beginPath();
        const hr = SUBSTRATE_R * 0.85;
        for (let i = 0; i < 6; i++) {
            const a = (Math.PI / 3) * i;
            ctx.lineTo(hr * Math.cos(a), hr * Math.sin(a));
        }
        ctx.closePath();
        ctx.fillStyle = getC('--prod-color'); ctx.strokeStyle = config.theme==='paper'?"#333":"#111"; ctx.lineWidth = 1;
        ctx.fill(); ctx.stroke();
        ctx.restore();
    }
    move(factor, width, height, padding) {
        super.move(factor * 0.45, width, height, padding);
    }
}

function drawSubstrateShape(ctx, cx, cy, r, color) {
    ctx.save();
    ctx.translate(cx, cy);
    const hr = r * 0.85;
    const hx1 = -hr * 0.95;
    const hx2 = hr * 0.95;
    const outline = config.theme==='paper'?"#333":"#111";
    ctx.beginPath();
    ctx.moveTo(hx1, 0); ctx.lineTo(hx2, 0);
    ctx.strokeStyle = outline; ctx.lineWidth = 1.5; ctx.stroke();
    const drawHex = (x) => {
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const a = (Math.PI / 3) * i;
            ctx.lineTo(x + hr * Math.cos(a), hr * Math.sin(a));
        }
        ctx.closePath();
        ctx.fillStyle = color; ctx.strokeStyle = outline; ctx.lineWidth = 1;
        ctx.fill(); ctx.stroke();
    };
    drawHex(hx1); drawHex(hx2);
    ctx.restore();
}

// --- Denaturation Logistics ---
function updateDenatThresholds() {
    let denatFrac = 0;
    let temp = config.temp;
    let thermo = config.thermostable;
    
    if (thermo) {
        if (temp >= 90) denatFrac = 1.0;
        else if (temp >= 70) denatFrac = (temp - 70) / 20.0;
    } else {
        if (temp >= 60) denatFrac = 1.0;
        else if (temp >= 40) denatFrac = 0.25 + 0.75 * ((temp - 40) / 20.0);
    }
    
    let nEnz = enzymes.length;
    if (nEnz === 0) return;
    
    let numToDenature = Math.round(nEnz * denatFrac);
    for (let e of enzymes) {
        e.denatureThreshold = null;
        e.denatured = false;
    }
    
    // Choose random enzymes to denature
    let shuffled = [...enzymes].sort(() => 0.5 - Math.random());
    let toDenature = shuffled.slice(0, numToDenature);
    
    let remaining = substrates.length;
    if (remaining === 0) remaining = config.numSubstrates;
    
    for (let e of toDenature) {
        if (temp >= (thermo ? 90 : 60)) {
            e.denatureThreshold = Infinity;
        } else {
            e.denatureThreshold = Math.random() * (remaining - 4) + 4;
        }
    }
}

// --- App Control ---
function init() {
    updateCanvasSize();
    graphCanvas.width = graphCanvas.parentElement.clientWidth;
    graphCanvas.height = 250;
    resetSim();
    requestAnimationFrame(loop);
}

function resetSim() {
    running = false;
    enzymes = []; substrates = []; products = [];
    reactionsDone = 0; winTime = 0.0; accumulatedTime = 0.0; lastTickTime = 0;
    finishTimer = 0;
    config.hasSavedData = false;
    config.hasRecordedRate = false;
    config.recordedRate = 0;
    
    document.getElementById('btnStart').innerHTML = "▶ START";
    document.getElementById('graphOverlay').style.display = dataPoints.length ? "none" : "block";

    for (let i = 0; i < config.numEnzymes; i++) {
        let e = new Enzyme(Math.random() * canvas.width, Math.random() * canvas.height);
        enzymes.push(e);
    }
    for (let i = 0; i < config.numSubstrates; i++) {
        substrates.push(new Substrate(Math.random() * canvas.width, Math.random() * canvas.height));
    }
    
    updateDenatThresholds();
    enzymes.forEach(e => e.checkDenaturation(substrates.length, config.temp, config.thermostable));
    
    updateStats();
    drawBeaker();
    drawGraph();
}

function updateStats() {
    document.getElementById('statReactions').textContent = reactionsDone;
    document.getElementById('statSubstrate').textContent = substrates.length;
    let rate = 0;
    if (winTime >= 0.5 && substrates.length > 0) {
        rate = reactionsDone / winTime;
        document.getElementById('statRate').textContent = rate.toFixed(1);
    } else if (winTime === 0) {
        document.getElementById('statRate').textContent = "-";
    }
}

function loop(t) {
    if (!lastTickTime) lastTickTime = t;
    const realDt = (t - lastTickTime) / 1000.0; // Seconds
    lastTickTime = t;

    if (running) {
        const logicFac = rgtFactor(config.temp) * config.simSpeed;
        const dt = realDt * config.simSpeed;
        const ticks = realDt / 0.03; // Framerate independent ticks (1 tick = 30ms)
        const moveFac = logicFac * Math.min(ticks, 3); // cap to avoid skipping
        
        let remaining = substrates.length;
        
        // Update Enzymes
        for (let e of enzymes) {
            e.checkDenaturation(remaining, config.temp, config.thermostable);
            if (e.bindingTimer > 0) {
                e.bindingTimer -= ticks; // decrease based on real time passed
            } else {
                e.move(moveFac, canvas.width, canvas.height, ENZYME_R + 4);
            }
        }

        // Update Substrates & Collisions
        let newRx = 0;
        
        for (let s of substrates) {
            if (s.reacted) continue;
            s.move(moveFac, canvas.width, canvas.height, enzymes, remaining, SUBSTRATE_R + 4);
            for (let e of enzymes) {
                if (!e.denatured && e.bindingTimer <= 0) {
                    if (Math.hypot(s.x - e.x, s.y - e.y) < COLL_DIST) {
                        s.reacted = true;
                        e.bindingTimer = Math.max(2, 6 / logicFac); // Lock enzyme
                        newRx++;
                        // Create 2 products
                        products.push(new Product(s.x + (Math.random()-0.5)*10, s.y + (Math.random()-0.5)*10));
                        products.push(new Product(s.x + (Math.random()-0.5)*10, s.y + (Math.random()-0.5)*10));
                        break;
                    }
                }
            }
        }
        
        reactionsDone += newRx;
        substrates = substrates.filter(s => !s.reacted);
        
        for (let p of products) p.move(moveFac, canvas.width, canvas.height, SUBSTRATE_R + 4);
        
        if (remaining > 0) {
            accumulatedTime += dt;
            winTime += dt;
        }
        
        // Record initial rate at 50% (Snapped perfectly to mathematical curve)
        if (!config.hasRecordedRate && (reactionsDone >= initialSubstratesCount * 0.5 || remaining === 0)) {
            if (accumulatedTime > 0) {
                config.recordedRate = reactionsDone / accumulatedTime; // Empirical rate
                config.hasRecordedRate = true;
            }
        }
        
        // At the very end of the simulation, wait 1 second before stopping
        if (substrates.length === 0) {
            finishTimer += realDt;
            
            if (finishTimer >= 1.0) {
                running = false;
                document.getElementById('btnStart').innerHTML = "✓ FERTIG";
                
                if (config.hasRecordedRate && !config.hasSavedData) {
                    let theoryRate = mmRate(initialSubstratesCount, config.numEnzymes, config.temp, config.thermostable);
                    dataPoints.push([initialSubstratesCount, theoryRate, config.numEnzymes, config.temp]);
                    config.hasSavedData = true;
                    drawGraph();
                }
            }
        }
        
        updateStats();
    }
    
    drawBeaker();
    requestAnimationFrame(loop);
}

function drawBeaker() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Water
    ctx.fillStyle = getC('--water-bg');
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Grid
    ctx.strokeStyle = getC('--grid-color'); ctx.lineWidth = 1;
    const gridSp = 20 * scale;
    ctx.beginPath();
    for (let x = 0; x <= canvas.width; x += gridSp) { ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); }
    for (let y = 0; y <= canvas.height; y += gridSp) { ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); }
    ctx.stroke();
    
    ctx.strokeStyle = getC('--thermo-ol');
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, canvas.width, canvas.height);

    // Temp Text
    const tMid = config.thermostable ? DENATURE_THERMO : DENATURE_NORMAL;
    ctx.fillStyle = config.temp > tMid - 10 ? getC('--error-color') : getC('--text-color');
    ctx.font = `bold ${Math.max(12, 14*scale)}px ${getC('--font-family')}`;
    ctx.textAlign = "left";
    ctx.fillText(`T = ${config.temp.toFixed(0)} °C`, 10*scale, 20*scale);

    // Thermometer
    const thX = canvas.width - 20*scale; const thY = 20*scale;
    const h = 40*scale;
    ctx.fillStyle = getC('--thermo-bg'); ctx.strokeStyle = getC('--thermo-ol');
    ctx.fillRect(thX - 3, thY, 6, h); ctx.strokeRect(thX - 3, thY, 6, h);
    const fillH = Math.min(h, Math.max(2, h * config.temp / 100));
    ctx.fillStyle = config.temp > tMid - 10 ? getC('--error-color') : getC('--temp-cool');
    ctx.fillRect(thX - 2, thY + h - fillH, 4, fillH);
    ctx.beginPath(); ctx.arc(thX, thY + h + 4*scale, 6*scale, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

    // Particles
    for (let p of products) p.draw(ctx);
    for (let s of substrates) s.draw(ctx);
    for (let e of enzymes) e.draw(ctx);
}

function drawGraph() {
    gctx.clearRect(0, 0, graphCanvas.width, graphCanvas.height);
    
    gctx.fillStyle = getC('--graph-bg');
    gctx.fillRect(0, 0, graphCanvas.width, graphCanvas.height);
    
    const w = graphCanvas.width; const h = graphCanvas.height;
    const pl = 65, pr = 20, pt = 25, pb = 55;
    const gw = w - pl - pr; const gh = h - pt - pb;
    
    graphHitRegions = [];

    // Background Grid
    gctx.strokeStyle = getC('--grid-color'); gctx.lineWidth = 1;
    gctx.beginPath();
    for(let i=1; i<4; i++) {
        let y = pt + gh * i / 4; gctx.moveTo(pl, y); gctx.lineTo(pl + gw, y);
        let x = pl + gw * i / 4; gctx.moveTo(x, pt); gctx.lineTo(x, pt + gh);
    }
    gctx.stroke();

    // Axes
    gctx.strokeStyle = getC('--muted-color'); gctx.lineWidth = 2;
    gctx.beginPath();
    gctx.moveTo(pl, pt); gctx.lineTo(pl, pt + gh); gctx.lineTo(pl + gw, pt + gh);
    gctx.stroke();

    // Labels
    gctx.fillStyle = getC('--muted-color'); gctx.font = `14px ${getC('--font-family')}`;
    gctx.textAlign = "center";
    gctx.fillText("Substratkonzentration [S]", pl + gw/2, h - 12);
    
    gctx.save();
    gctx.translate(pl - 45, pt + gh/2);
    gctx.rotate(-Math.PI/2);
    gctx.fillText("Reaktionsgeschwindigkeit", 0, 0);
    gctx.restore();

    let configsSet = new Set(dataPoints.map(p => `${p[2]},${p[3]}`));
    configsSet.add(`${config.numEnzymes},${config.temp}`);
    let configs = Array.from(configsSet).map(s => { let p = s.split(','); return [parseInt(p[0]), parseFloat(p[1])]; }).sort();

    let maxS = Math.max(200, config.numSubstrates);
    if (dataPoints.length) maxS = Math.max(maxS, ...dataPoints.map(p => p[0]));

    let vmaxDict = {};
    for (let c of configs) vmaxDict[`${c[0]},${c[1]}`] = mmRate(150.0, c[0], c[1], config.thermostable);
    
    let globalMaxVmax = Object.values(vmaxDict).length ? Math.max(...Object.values(vmaxDict)) : 0;
    let maxR = Math.max(globalMaxVmax * 1.15, 0.5);

    const curveColorsStr = getC('--curve-colors');
    const curveColors = curveColorsStr ? curveColorsStr.split(',').map(s=>s.trim()) : ["#58a6ff", "#f78166", "#3fb950", "#d2a8ff", "#e3b341", "#8abeb7"];

    if (config.showCurve) {
        const steps = 200;
        configs.forEach((cfg, idx) => {
            const [ne, t] = cfg;
            const col = curveColors[idx % curveColors.length];
            const ptsForCfg = dataPoints.filter(p => p[2] === ne && p[3] === t);
            const maxSim = ptsForCfg.length ? Math.max(...ptsForCfg.map(p => p[0])) : 0;
            const vmaxVal = vmaxDict[`${ne},${t}`];
            const maxRate = ptsForCfg.length ? Math.max(...ptsForCfg.map(p => p[1])) : 0;
            
            if (maxSim > 0) {
                gctx.beginPath();
                gctx.strokeStyle = col; gctx.lineWidth = 2.5;
                for (let i = 0; i <= steps; i++) {
                    let s = maxSim * i / steps;
                    let v = mmRate(s, ne, t, config.thermostable);
                    let x = pl + (s / maxS) * gw;
                    let y = pt + gh - Math.min(v / maxR, 1.0) * gh;
                    if (i === 0) gctx.moveTo(x, y); else gctx.lineTo(x, y);
                }
                gctx.stroke();
            }

            // Vmax line
            if (maxRate >= vmaxVal * 0.97) {
                const vy = pt + gh - Math.min(vmaxVal / maxR, 1.0) * gh;
                gctx.beginPath(); gctx.setLineDash([6, 4]); gctx.moveTo(pl, vy); gctx.lineTo(pl + gw, vy);
                gctx.strokeStyle = col; gctx.lineWidth = 2; gctx.stroke(); gctx.setLineDash([]);
                gctx.fillStyle = col; gctx.textAlign = "right"; gctx.font = `12px ${getC('--font-family')}`;
                gctx.fillText(`V_max (${ne}E, ${t.toFixed(0)}°C)`, pl + gw - 4, vy - 8);
                
                // Hit region for Vmax
                graphHitRegions.push({
                    x: pl, y: vy - 15, w: gw, h: 25,
                    text: `<b>V<sub>max</sub> ≈ ${vmaxVal.toFixed(2)}</b> [Produkte/s]<br><small>(${ne} Enzyme, ${t.toFixed(0)}°C)</small>`
                });
                
                if (config.showKm) {
                    const kmVal = 20.0;
                    const kmX = pl + (kmVal / maxS) * gw;
                    const vyHalf = pt + gh - Math.min((vmaxVal/2) / maxR, 1.0) * gh;
                    const kmCol = getC('--km-color');
                    
                    gctx.beginPath(); gctx.setLineDash([2, 2]);
                    gctx.moveTo(pl, vyHalf); gctx.lineTo(kmX, vyHalf);
                    gctx.lineTo(kmX, pt + gh);
                    gctx.strokeStyle = kmCol; gctx.lineWidth = 1.5; gctx.stroke(); gctx.setLineDash([]);
                    gctx.fillStyle = kmCol; gctx.textAlign = "right";
                    gctx.fillText("V_max/2", pl - 4, vyHalf + 4);
                    gctx.textAlign = "center";
                    gctx.fillText("K_m", kmX, pt + gh + 14);

                    // Hit regions for Km
                    graphHitRegions.push({
                        x: kmX - 15, y: vyHalf, w: 30, h: (pt + gh) - vyHalf + 20,
                        text: `<b>K<sub>m</sub> = ${kmVal.toFixed(1)}</b> [Substrat]<br><small>Konzentration bei V<sub>max</sub>/2</small>`
                    });
                    graphHitRegions.push({
                        x: pl - 50, y: vyHalf - 10, w: 50, h: 20,
                        text: `<b>V<sub>max</sub> / 2 ≈ ${(vmaxVal/2).toFixed(2)}</b>`
                    });
                }
            }
        });
    }

    if (dataPoints.length > 0) {
        document.getElementById('graphOverlay').style.display = 'none';
        dataPoints.forEach(p => {
            const [sCnt, rate, ne, t] = p;
            let x = pl + (sCnt / maxS) * gw;
            let y = pt + gh - Math.min(rate / maxR, 1.0) * gh;
            let idx = configs.findIndex(c => c[0] === ne && c[1] === t);
            let col = curveColors[idx % curveColors.length];
            gctx.beginPath(); gctx.arc(x, y, 4, 0, Math.PI * 2);
            gctx.fillStyle = col; gctx.fill(); gctx.strokeStyle = getC('--bg-color'); gctx.lineWidth = 1.5; gctx.stroke();
        });
    } else {
        document.getElementById('graphOverlay').style.display = 'block';
    }

    gctx.fillStyle = getC('--muted-color'); gctx.textAlign = "center";
    gctx.font = `12px ${getC('--font-family')}`;
    gctx.fillText("0", pl, pt + gh + 22);
    gctx.fillText(Math.floor(maxS).toString(), pl + gw, pt + gh + 22);
    gctx.textAlign = "right";
    gctx.fillText(maxR.toFixed(1), pl - 8, pt + 6);
}

// --- UI Binding ---
function updateUI() {
    const f = rgtFactor(config.temp);
    document.getElementById('rgtText').textContent = `RGT-Faktor: ${f.toFixed(2)}x (Basis 25 °C)`;
    
    const tMid = config.thermostable ? DENATURE_THERMO : DENATURE_NORMAL;
    const warn = document.getElementById('denatWarning');
    if (config.temp >= tMid + 10) warn.textContent = "⚠ Alle Enzyme denaturiert!";
    else if (config.temp > tMid - 10) warn.textContent = "⚠ Enzyme denaturieren zunehmend!";
    else warn.textContent = "";

    document.getElementById('tempInput').value = config.temp;
    document.getElementById('tempValueDisplay').textContent = config.temp;
    document.getElementById('tempSlider').value = config.temp;
    
    document.getElementById('enzInput').value = config.numEnzymes;
    document.getElementById('subInput').value = config.numSubstrates;
    document.getElementById('enzDisplay').textContent = config.numEnzymes;
    document.getElementById('subDisplay').textContent = config.numSubstrates;
    
    updateDenatThresholds();
    enzymes.forEach(e => e.checkDenaturation(substrates.length, config.temp, config.thermostable));
    drawBeaker(); drawGraph();
}

document.getElementById('tempSlider').addEventListener('input', e => {
    config.temp = parseFloat(e.target.value);
    updateUI();
});

document.getElementById('tempInput').addEventListener('change', e => {
    config.temp = Math.max(0, Math.min(100, parseFloat(e.target.value) || 25));
    updateUI();
});

document.getElementById('btnTempMinus').addEventListener('click', () => {
    config.temp = Math.max(0, config.temp - 1);
    updateUI();
});

document.getElementById('btnTempPlus').addEventListener('click', () => {
    config.temp = Math.min(100, config.temp + 1);
    updateUI();
});

document.getElementById('enzSlider').addEventListener('input', e => {
    config.numEnzymes = parseInt(e.target.value);
    updateUI(); if(!running) resetSim();
});

document.getElementById('enzInput').addEventListener('change', e => {
    let val = Math.max(1, Math.min(20, parseInt(e.target.value) || 4));
    config.numEnzymes = val; document.getElementById('enzSlider').value = val;
    updateUI(); if(!running) resetSim();
});

document.getElementById('btnEnzMinus').addEventListener('click', () => {
    let val = Math.max(1, config.numEnzymes - 1);
    config.numEnzymes = val; document.getElementById('enzSlider').value = val;
    updateUI(); if(!running) resetSim();
});

document.getElementById('btnEnzPlus').addEventListener('click', () => {
    let val = Math.min(20, config.numEnzymes + 1);
    config.numEnzymes = val; document.getElementById('enzSlider').value = val;
    updateUI(); if(!running) resetSim();
});

document.getElementById('subSlider').addEventListener('input', e => {
    config.numSubstrates = parseInt(e.target.value);
    updateUI(); if(!running) resetSim();
});

document.getElementById('subInput').addEventListener('change', e => {
    let val = Math.max(1, Math.min(200, parseInt(e.target.value) || 100));
    config.numSubstrates = val; document.getElementById('subSlider').value = val;
    updateUI(); if(!running) resetSim();
});

document.getElementById('btnSubMinus').addEventListener('click', () => {
    let val = Math.max(1, config.numSubstrates - 1);
    config.numSubstrates = val; document.getElementById('subSlider').value = val;
    updateUI(); if(!running) resetSim();
});

document.getElementById('btnSubPlus').addEventListener('click', () => {
    let val = Math.min(200, config.numSubstrates + 1);
    config.numSubstrates = val; document.getElementById('subSlider').value = val;
    updateUI(); if(!running) resetSim();
});

document.getElementById('speedSlider').addEventListener('input', e => {
    config.simSpeed = parseFloat(e.target.value);
});

// Custom Checkboxes
function toggleCheck(id, prop, callback) {
    const el = document.getElementById(id);
    config[prop] = !config[prop];
    if (config[prop]) el.classList.add('checked'); else el.classList.remove('checked');
    if (callback) callback();
}

document.getElementById('thermoCheckRow').onclick = () => toggleCheck('thermoCheckbox', 'thermo', () => {
    config.thermostable = config.thermo;
    updateUI();
});

document.getElementById('curveCheckRow').onclick = () => toggleCheck('curveCheckbox', 'showCurve', () => {
    if (config.showCurve) {
        document.getElementById('kmCheckRow').style.pointerEvents = 'auto';
        document.getElementById('kmCheckRow').style.opacity = '1.0';
    } else {
        document.getElementById('kmCheckRow').style.pointerEvents = 'none';
        document.getElementById('kmCheckRow').style.opacity = '0.5';
        if (config.showKm) toggleCheck('kmCheckbox', 'showKm');
    }
    drawGraph();
});

document.getElementById('kmCheckRow').onclick = () => {
    if (config.showCurve) toggleCheck('kmCheckbox', 'showKm', drawGraph);
};



// Theme Switcher Logic
function applyTheme(themeName) {
    config.theme = themeName;
    document.body.className = "theme-" + themeName;
    if (themeName === 'dark') {
        document.getElementById('btnDark').classList.add('active-dark');
        document.getElementById('btnPaper').classList.remove('active-paper');
    } else {
        document.getElementById('btnDark').classList.remove('active-dark');
        document.getElementById('btnPaper').classList.add('active-paper');
    }
    // Need small delay for layout/css updates before redrawing canvas
    setTimeout(() => {
        drawBeaker();
        drawGraph();
    }, 50);
}

document.getElementById('btnDark').onclick = () => applyTheme('dark');
document.getElementById('btnPaper').onclick = () => applyTheme('paper');

document.getElementById('btnStart').onclick = () => {
    running = !running;
    const btn = document.getElementById('btnStart');
    if (running) {
        if (reactionsDone === 0 && accumulatedTime === 0) {
            initialSubstratesCount = substrates.length;
            config.hasSavedData = false;
            config.hasRecordedRate = false;
        }
        lastTickTime = performance.now();
        btn.innerHTML = "⏸ PAUSE";
    } else {
        btn.innerHTML = "▶ WEITER";
    }
};

document.getElementById('btnReset').onclick = resetSim;
document.getElementById('btnGraphClear').onclick = () => { dataPoints = []; drawGraph(); };

// Start
init();

// --- Tooltip Logic ---
const tooltip = document.getElementById('tooltip');
const mainTitle = document.getElementById('mainTitle');

mainTitle.addEventListener('mouseenter', (e) => {
    const text = mainTitle.getAttribute('data-tooltip');
    tooltip.innerHTML = text;
    tooltip.style.display = 'block';
});

mainTitle.addEventListener('mousemove', (e) => {
    tooltip.style.left = (e.pageX + 15) + 'px';
    tooltip.style.top = (e.pageY + 15) + 'px';
});

mainTitle.addEventListener('mouseleave', () => {
    tooltip.style.display = 'none';
});

// --- Graph Tooltip Logic ---
graphCanvas.addEventListener('mousemove', (e) => {
    const rect = graphCanvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    
    let found = null;
    // Search backwards to get the top-most (newest) region
    for (let i = graphHitRegions.length - 1; i >= 0; i--) {
        const r = graphHitRegions[i];
        if (mx >= r.x && mx <= r.x + r.w && my >= r.y && my <= r.y + r.h) {
            found = r;
            break;
        }
    }
    
    if (found) {
        tooltip.innerHTML = found.text;
        tooltip.style.display = 'block';
        tooltip.style.left = (e.pageX + 15) + 'px';
        tooltip.style.top = (e.pageY + 15) + 'px';
        graphCanvas.style.cursor = 'help';
    } else {
        tooltip.style.display = 'none';
        graphCanvas.style.cursor = 'default';
    }
});

graphCanvas.addEventListener('mouseleave', () => {
    tooltip.style.display = 'none';
    graphCanvas.style.cursor = 'default';
});
