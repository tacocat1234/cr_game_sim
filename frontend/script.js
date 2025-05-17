let hovered = null;
let selected = null;
let drag_start_pos = null;
let elixir = 7;
let state = "home";
let place = false;
let info = null; //json promise(?)
const my_id = generateUUID();
const frame_duration = 1/24 * 1000;

let tips = ["This game's logic was coded in Python!", 
    "Well? Did you?", "Knight has good stats for its cost.",
    "HTML is really annoying to work with.",
    "Hello, World.", "APCSA is a really boring class.",
    "OOP is better.", "Sometimes the cards cheat, and I don't know why or how.",
    "Apparently, making sprites for things is hard."]
let t_i = 0;
for (let i = tips.length - 1; i > 0; i--) { //shuffle
    const j = Math.floor(Math.random() * (i + 1));
    [tips[i], tips[j]] = [tips[j], tips[i]]; // Swap elements
}
let inter = null; //interval obj
let post_inter = null;
let fetch_inter = null;
deck = [["battleram", 11],
        ["skeletons", 11],
        ["cannon", 11],
        ["babydragon", 11],
        ["electrospirit", 11],
        ["barbarianbarrel", 11],
        ["zap", 11],
        ["icegolem", 11],
        ["kingtower", 11],
        ["daggerduchess", 11]];

let hand = [0, 1, 2, 3];
let cycler = [4, 5, 6, 7];
let promise_index = null;

const gameDisplay = document.getElementById('gameDisplay');
const lobbyForm = document.getElementById('lobbyForm');
const newRandom = document.getElementById('newRandom');
const createSpecific = document.getElementById('createSpecific');
const joinSpecific = document.getElementById('joinSpecific');

const ctx = gameDisplay.getContext('2d');
//const debug = document.getElementById("debug");

const bg = new Image(); bg.src = "../sprites/background.png";
const select = new Image(); select.src = "../sprites/tileselect.png";

let resizeTimeout;
let scale = window.innerHeight/768;

handleResize(); //init resize
draw(); //start loop


window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(handleResize, 100); // Debounce delay: 100ms
});

lobbyForm.addEventListener('submit', () => {
    if (state == "join_screen"){
        joinSpecificLobby();
    }
    else if (state == "create_screen"){
        createSpecificLobby();
    }
    else alert("Illegal state tracker result");
});

newRandom.addEventListener('click', () => {
    if (state == "home"){
        findRandom();
    }
});

createSpecific.addEventListener('click', () => {
    if (state == "home"){
        state = "create_screen";
        showLobbyPopup();
    }
});

joinSpecific.addEventListener('click', () => {
    if (state == "home"){
        state = "join_screen";
        showLobbyPopup();
    }
})

document.getElementById('closePop').addEventListener('click', () => {
    state = "home";
    hideLobbyPopup();
})

document.getElementById('cancelWait').addEventListener('click', () => {
    delete_arena();
    state = "home";
    showHome();
    hideWaiting();
})

function cycle(hand, index, queue) {
    queue.push(hand[index]);
    hand[index] = queue.shift();
}

function generateUUID() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

function handleResize(){
    scale = window.innerHeight/768;
    gameDisplay.style.height = scale * 768 + "px";
    gameDisplay.style.width = scale * 488 + "px";
    gameDisplay.width = Math.floor(scale * 488);
    gameDisplay.height = Math.floor(scale * 768);
}

function showLobbyPopup(){
    document.getElementById('lobbyPop').style.display = "block";
}

function hideLobbyPopup(){
    document.getElementById('lobbyPop').style.display = "none";
}

function showGame(){
    document.getElementById('gamePage').style.display = "block";
}

function hideGame(){
    document.getElementById('gamePage').style.display = "none";
}

function showHome(){
    document.getElementById('homePage').style.display = "block";
}

function hideHome(){
    document.getElementById('homePage').style.display = "none";
}

function showWaiting(){
    loadTips();
    document.getElementById('waitingPage').style.display = "block";
}

function hideWaiting(){
    clearTips();
    document.getElementById('waitingPage').style.display = "none";
}

function findRandom(){
    let server_return = join_random(my_id, deck[9][0], deck[9][1]);
    if (!server_return["confirm"]){ //if no valid or otherwise cannot join
        server_return = new_game(my_id, deck[9][0], deck[9][1]); //create
        if (server_return["confirm"] !== true){
            alert(server_return["err"]); //unsuccesful create
        }
        else {
            state = "lobby_wait";
            showWaiting();
            hideHome();
        }
    }
    else {
        state = "game";
        showGame();
        hideWaiting();
        hideHome();
    }
}

function createSpecificLobby(){
    let server_return = new_game(my_id, deck[9][0], deck[9][1], false, document.getElementById('lobbyName').value);
    if (server_return["confirm"] !== true){
        alert(server_return["err"]);
    }
    else {
        state = "lobby_wait";
        showWaiting();
        hideHome();
    }
}

function joinSpecificLobby(){
    let server_return = join_specific(my_id, document.getElementById('lobbyName').value, deck[9][0], deck[9][1], true);
    if (server_return["confirm"] !== true){
        alert(server_return["err"]);
    }
    else {
        state = "game";
        showGame();
        hideWaiting();
        hideHome();
    }
}

function draw(){
    if (state == "game"){
        ctx.drawImage(bg, 64 * scale, 0, 360 * scale, 640 * scale);
    }
    requestAnimationFrame(draw);
}

function loadTips(){
    inter = setInterval(() => {
        document.getElementById('tips').textContent = tips[t_i];
        t_i++;
        t_i = t_i >= tips.length ? 0 : t_i;
    }, 2000);
}

function clearTips(){
    clearInterval(inter);
}

function postLoop(){
    post_inter = setInterval(() => {
        if (place){ //
            let wid = scale * 488;
            let selected_card_index = null;
            if (drag_start_pos[0] < wid/10 + wid/5) selected_card_index = 0;
            else if (drag_start_pos[0] < wid/10 + 2*wid/5) selected_card_index = 1;
            else if (drag_start_pos[0] < wid/10 + 3*wid/5) selected_card_index = 2;
            else selected_card_index = 3;
            if (hand[selected_card_index][1] <= elixir){
                spawn_card(hand[selected_card_index][0], POSTEMP, hand[selected_card_index][1]) //consider storign elixir on server side
            }
        }
    }, frame_duration)
}

function fetchLoop(){
    fetch_inter = setInterval(() => {
        info = get_info();
    }, frame_duration)
}