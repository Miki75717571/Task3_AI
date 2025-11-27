// Simple 15-puzzle viewer
const MOVES = { U: [-1, 0], D: [1, 0], L: [0, -1], R: [0, 1] };

let R = 4, C = 4;
let states = []; // sequence of states (each is array)
let cur = 0;
let timer = null;

const el = id => document.getElementById(id);

function parseInitial(text){
	const parts = text.trim().split(/\n+/).map(l=>l.trim()).filter(Boolean);
	if(parts.length === 0) return null;
	const first = parts[0].split(/\s+/).map(Number);
	if(first.length >= 2){
		R = first[0]; C = first[1];
		const nums = parts.slice(1).join(' ').split(/\s+/).map(Number).filter(n=>!Number.isNaN(n));
		if(nums.length !== R*C) return null;
		return nums;
	} else {
		return null;
	}
}

function parseSolverOutput(text){
	const parts = text.trim().split(/\n+/).map(l=>l.trim());
	if(parts.length < 2) return {n:0, moves:''};
	const n = parseInt(parts[0]) || 0;
	const moves = parts[1].trim();
	return {n, moves};
}

function renderGrid(state){
	const grid = el('grid');
	grid.innerHTML = '';
	grid.style.gridTemplateColumns = `repeat(${C}, 60px)`;
	for(let i=0;i<state.length;i++){
		const d = state[i];
		const div = document.createElement('div');
		div.className = 'cell' + (d===0? ' blank':'');
		div.textContent = d===0? '': d;
		grid.appendChild(div);
	}
}

function applyMoveToState(stateArr, move){
	// stateArr is array of length R*C
	const zeroIdx = stateArr.indexOf(0);
	const zr = Math.floor(zeroIdx / C), zc = zeroIdx % C;
	const [dr, dc] = MOVES[move] || [0,0];
	const nr = zr + dr, nc = zc + dc;
	if(nr < 0 || nr >= R || nc < 0 || nc >= C) return null;
	const nidx = nr * C + nc;
	const copy = stateArr.slice();
	copy[zeroIdx] = copy[nidx];
	copy[nidx] = 0;
	return copy;
}

function buildStates(initial, moves){
	const seq = [];
	seq.push(initial.slice());
	let curState = initial.slice();
	for(const m of moves){
		const ns = applyMoveToState(curState, m);
		if(ns === null) break;
		seq.push(ns);
		curState = ns;
	}
	return seq;
}

function updateStatus(){
	el('status').textContent = `Step ${cur}/${states.length-1}`;
}

function showCur(){
	if(states.length === 0) return;
	renderGrid(states[cur]);
	el('jumpIdx').value = cur;
	updateStatus();
}

function doLoad(){
	const init = parseInitial(el('initialInput').value);
	if(!init){ alert('Cannot parse initial input. Use format: first line "R C" then R rows of C numbers.'); return; }
	const out = parseSolverOutput(el('solverOutput').value);
	const moves = out.moves || '';
	// validate moves
	if(!/^[UDLR]*$/.test(moves)){
		alert('Moves contain invalid characters. Only U,D,L,R allowed.');
		return;
	}
	states = buildStates(init, moves);
	cur = 0;
	showCur();
}

function doReset(){
	if(states.length>0){ cur = 0; showCur(); }
}

function stepNext(){
	if(states.length === 0) return;
	if(cur < states.length-1) cur++; showCur();
}

function stepPrev(){
	if(states.length === 0) return;
	if(cur > 0) cur--; showCur();
}

function playPause(){
	if(timer){ clearInterval(timer); timer = null; el('playBtn').textContent = '► Play'; return; }
	const interval = parseInt(el('speed').value) || 300;
	el('playBtn').textContent = '❚❚ Pause';
	timer = setInterval(()=>{
		if(cur >= states.length-1){ clearInterval(timer); timer=null; el('playBtn').textContent = '► Play'; return; }
		cur++; showCur();
	}, interval);
}

function jumpTo(){
	const v = parseInt(el('jumpIdx').value) || 0;
	if(v < 0 || v >= states.length) { alert('Index out of range'); return; }
	cur = v; showCur();
}

// Wire events
document.addEventListener('DOMContentLoaded', ()=>{
	el('loadBtn').addEventListener('click', doLoad);
	el('resetBtn').addEventListener('click', doReset);
	el('nextBtn').addEventListener('click', stepNext);
	el('prevBtn').addEventListener('click', stepPrev);
	el('playBtn').addEventListener('click', playPause);
	el('jumpBtn').addEventListener('click', jumpTo);
	el('jumpIdx').addEventListener('change', jumpTo);
	// file input for loading viewer JSON saved by solver
	const fileIn = el('fileIn');
	if(fileIn){
		fileIn.addEventListener('change', (ev)=>{
			const f = ev.target.files[0];
			if(!f) return;
			const reader = new FileReader();
			reader.onload = (e)=>{
				try{
					const obj = JSON.parse(e.target.result);
					loadFromPayload(obj);
				}catch(err){ alert('Invalid JSON file'); }
			};
			reader.readAsText(f, 'utf-8');
		});
	}

	// Check URL payload (base64 JSON) when opened via solver --open-viewer
	try{
		const qs = new URLSearchParams(window.location.search);
		if(qs.has('payload')){
			const b64 = qs.get('payload');
			if(b64){
				try{
					const jsonStr = atob(decodeURIComponent(b64));
					const obj = JSON.parse(jsonStr);
					loadFromPayload(obj);
				}catch(e){
					console.error('Failed to parse payload', e);
				}
			}
		}
	}catch(e){ console.error(e); }
	// sample default
	el('initialInput').value = '4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 15 0';
	el('solverOutput').value = '0\n';
	// default load will be skipped if payload loaded
	if(!window.__viewer_payload_loaded) doLoad();
});

function loadFromPayload(obj){
	// expected keys: R, C, initial (array), solution_moves (string)
	try{
		if(typeof obj.R === 'number' && Array.isArray(obj.initial)){
			const firstLine = `${obj.R} ${obj.C}`;
			// build rows
			let rows = [];
			for(let r=0;r<obj.R;r++){
				const row = obj.initial.slice(r*obj.C,(r+1)*obj.C).join(' ');
				rows.push(row);
			}
			el('initialInput').value = firstLine + '\n' + rows.join('\n');
		}
		if(typeof obj.solution_moves === 'string'){
			const moves = obj.solution_moves || '';
			const n = moves.length >= 0 ? moves.length : (obj.solution_length || 0);
			el('solverOutput').value = `${n}\n${moves}`;
		}
		window.__viewer_payload_loaded = true;
		doLoad();
	}catch(e){ console.error('Failed to load payload', e); }
}

