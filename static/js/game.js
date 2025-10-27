let socket = null;
let gameState = { tokens: [], dice: ['white','white','white','white'], roll_history: [], white_count: 0, move_count: 0 };

const canvas = document.getElementById('gameBoard');
const ctx = canvas.getContext('2d');
const GRID_SIZE = 5, CELL_SIZE = 120, TOKEN_RADIUS = 15;
const X_POSITIONS = [[0,2],[2,0],[2,2],[2,4],[4,2]];

let draggingToken = null, dragOffsetX = 0, dragOffsetY = 0;

function submitPassword() {
    const password = document.getElementById("passwordInput").value;
    socket = io({ reconnection: false });

    socket.on("connect", () => socket.emit("auth", { password }));

    socket.on("auth_result", data => {
        if(data.success){
            document.getElementById("loginScreen").style.display = "none";
            document.getElementById("gameContainer").style.display = "block";
            socket.emit("request_state");
            attachGameListeners();
            attachDiceListeners();
            attachResetListener();
        } else {
            document.getElementById("loginMessage").textContent = "Incorrect password.";
            socket.disconnect();
        }
    });
}

function attachGameListeners(){
    socket.on('disconnect', () => updateConnectionStatus(false));
    socket.on('game_state', state => { gameState = state; updateUI(); drawBoard(); updateConnectionStatus(true); });
    socket.on('dice_rolled', (data) => {
        gameState.dice = data.dice;
        gameState.white_count = data.white_count;
        gameState.roll_history = data.roll_history;

        // Update dice visuals
        for(let i=0;i<4;i++){
            const die = document.getElementById(`die${i}`);
            die.className = 'die ' + gameState.dice[i]; // sets die0..die3 to "die white" or "die black"
        }

        updateUI();
        drawBoard();
    });

    socket.on('tokens_updated', data => { gameState.tokens=data.tokens; gameState.move_count=data.move_count; updateUI(); drawBoard(); });
    socket.on('game_reset', state => { gameState=state; draggingToken=null; drawBoard(); updateUI(); });
}

function attachDiceListeners(){
    document.querySelectorAll('.die').forEach(die=>die.addEventListener('click', ()=>{ if(socket) socket.emit('roll_dice'); }));
}

function attachResetListener(){
    document.getElementById('resetBtn').addEventListener('click', ()=>{ if(socket) socket.emit('reset_game'); });
}

function updateUI(){
    document.getElementById('whiteCount').textContent = gameState.white_count;
    document.getElementById('moveCount').textContent = gameState.move_count;
    const historyDiv = document.getElementById('rollHistory'); historyDiv.innerHTML='';
    gameState.roll_history.forEach(roll=>{
        const entry=document.createElement('div');
        entry.textContent = roll.dice.map(d=>'white'===d?'W':'B').join('') + ' → '+roll.count;
        historyDiv.appendChild(entry);
    });
}

function updateConnectionStatus(connected){
    const status=document.getElementById('status');
    status.textContent=connected?'Connected':'Disconnected';
    status.className=`connection-status ${connected?'connected':'disconnected'}`;
}

function drawBoard(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.strokeStyle='#666'; ctx.lineWidth=2;
    for(let i=0;i<=GRID_SIZE;i++){
        ctx.beginPath(); ctx.moveTo(i*CELL_SIZE,0); ctx.lineTo(i*CELL_SIZE,GRID_SIZE*CELL_SIZE); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0,i*CELL_SIZE); ctx.lineTo(GRID_SIZE*CELL_SIZE,i*CELL_SIZE); ctx.stroke();
    }
    ctx.strokeStyle='#333'; ctx.lineWidth=6;
    X_POSITIONS.forEach(([r,c])=>{
        const cx=c*CELL_SIZE+CELL_SIZE/2, cy=r*CELL_SIZE+CELL_SIZE/2, offset=CELL_SIZE/2-20;
        ctx.beginPath(); ctx.moveTo(cx-offset,cy-offset); ctx.lineTo(cx+offset,cy+offset); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx-offset,cy+offset); ctx.lineTo(cx+offset,cy-offset); ctx.stroke();
    });
    gameState.tokens.forEach(token=>{
        ctx.fillStyle=token.color;
        ctx.beginPath(); ctx.arc(token.x,token.y,TOKEN_RADIUS,0,Math.PI*2); ctx.fill();
        ctx.strokeStyle='#000'; ctx.lineWidth=2; ctx.stroke();
        if(draggingToken && draggingToken.id===token.id){ ctx.strokeStyle='#fff'; ctx.lineWidth=3; ctx.stroke(); }
    });
}

function startDragging(x,y){
    for(let i=gameState.tokens.length-1;i>=0;i--){
        const token=gameState.tokens[i], dx=x-token.x, dy=y-token.y;
        if(Math.sqrt(dx*dx+dy*dy)<=TOKEN_RADIUS){ draggingToken=token; dragOffsetX=dx; dragOffsetY=dy; break; }
    }
}

canvas.addEventListener('mousedown', e=>{
    const rect=canvas.getBoundingClientRect();
    startDragging(e.clientX-rect.left, e.clientY-rect.top);
});
canvas.addEventListener('mousemove', e=>{
    if(draggingToken){
        const rect=canvas.getBoundingClientRect();
        draggingToken.x=e.clientX-rect.left-dragOffsetX;
        draggingToken.y=e.clientY-rect.top-dragOffsetY;
        constrainToken(draggingToken);
        drawBoard();
    }
});
canvas.addEventListener('mouseup', sendTokenMove);
canvas.addEventListener('mouseleave', ()=>{ draggingToken=null; drawBoard(); });

canvas.addEventListener('touchstart', e=>{ e.preventDefault(); const rect=canvas.getBoundingClientRect(); const touch=e.touches[0]; startDragging(touch.clientX-rect.left, touch.clientY-rect.top); });
canvas.addEventListener('touchmove', e=>{ e.preventDefault(); if(draggingToken){ const rect=canvas.getBoundingClientRect(); const touch=e.touches[0]; draggingToken.x=touch.clientX-rect.left-dragOffsetX; draggingToken.y=touch.clientY-rect.top-dragOffsetY; constrainToken(draggingToken); drawBoard(); } });
canvas.addEventListener('touchend', e=>{ e.preventDefault(); sendTokenMove(); });

function constrainToken(token){
    token.x=Math.max(TOKEN_RADIUS,Math.min(canvas.width-TOKEN_RADIUS,token.x));
    token.y=Math.max(TOKEN_RADIUS,Math.min(canvas.height-TOKEN_RADIUS,token.y));
}

function sendTokenMove(){
    if(!draggingToken) return;
    socket.emit('move_token',{ token_id: draggingToken.id, x: draggingToken.x, y: draggingToken.y });
    draggingToken=null;
}

drawBoard();
