let hovered = null;
let selected = null;
let drag_start_pos = null;
let elixir = 7;
let state = "game";
const my_id = generateUUID();

deck = [["battleram", 11],
        ["skeletons", 11],
        ["cannon", 11],
        ["babydragon", 11],
        ["electrospirit", 11],
        ["barbarianbarrel", 11],
        ["zap", 11],
        ["icegolem", 11],
        ["kingtower", 11],
        ["daggerduchess", 11]]

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

newRandom.addEventListener('click', findRandom);

createSpecific.addEventListener('click', () => {
    state = "create_screen";
    showLobbyPopup();
});

joinSpecific.addEventListener('click', () => {
    state = "join_screen";
    showLobbyPopup();
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
    document.getElementById('waitingPage').style.display = "block";
}

function hideWaiting(){
    document.getElementById('waitingPage').style.display = "none";
}

function findRandom(){
    let server_return = join_random(my_id, deck[9][0], deck[9][1]);
    if (!server_return["confirm"]){ //if no valid or otherwise cannot join
        server_return = new_game(my_id, deck[9][0], deck[9][1]); //create
        if (!server_return["confirm"]){
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
    if (!server_return["confirm"]){
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
    if (!server_return["confirm"]){
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
    //let info = get_info();
    if (state == "game"){
        ctx.drawImage(bg, 64 * scale, 0, 360 * scale, 640 * scale);
    }
    requestAnimationFrame(draw);
}