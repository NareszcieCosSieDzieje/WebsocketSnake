
// websocket.addEventListener('close', () => {
//   window.location.reload(true);
// })

var websocket;


var clientID;

var maxFoodIteration = 1;

window.game_synchronized = true;

// var gridSize;
// var boardWidth;
// var boardHeight;
// var mySnake;
// var enemySnake; 
// var food;
// var iteration = 1;

const socketMessageListener = (event) => {

    data = JSON.parse(event.data);
  
    type = data['type']
    received_data = data['data']
  
    switch (type) {
      case 'connect':
        window.clientID = data.client_id;
        break;
      case 'game_init':
        window.gridSize = received_data.grid_size;
        window.boardWidth = received_data.board_width;
        window.boardHeight = received_data.board_height;
        window.mySnake = received_data[received_data.my_snake];
        window.enemySnake = received_data[received_data.enemy_snake];
        window.food = received_data.food;
        window.iteration = 1;
        startGame();
        break;
      case 'game_iter':
        if (received_data.iteration >= window.iteration) {
          window.enemySnake['direction'] = received_data.enemy_snake_direction
          // FIXME changeDirection(window.enemySnake, received_data.enemy_snake_dir)  DODAC TO JAK SIE ODBIERZE SYGNAL OD SERWERA
        }
        break;
      case 'new_food':
          if (received_data.iteration > maxFoodIteration) {
            maxFoodIteration = received_data.iteration;
            window.food['coordinates'] = received_data.new_food;
          }
        break;
      case 'synchronize':
          window.game_synchronized = true;
        break;
      case 'server_dead':
        // FIXME:
        break;
      default:
          console.error(
          "unsupported event", data);
    }
};
  

const socketOpenListener = (event) => {
  connect();
  console.log('Connected');
  // websocket.send('hello');
};

const socketCloseListener = (event) => {
  if (websocket) {
    console.error('Disconnected.');
  }
  websocket = new WebSocket('ws://127.0.0.1:6789/'); 
  websocket.addEventListener('open', socketOpenListener);
  websocket.addEventListener('message', socketMessageListener);
  websocket.addEventListener('close', socketCloseListener);
};


function checkSupported() {
  canvas = document.getElementById('canvas');
  if (canvas.getContext){
    window.ctx = canvas.getContext('2d');
  } else {
    alert("We're sorry, but your browser does not support the canvas tag. Please use any web browser other than Internet Explorer.");
  }
}

function connect() {
  message = {
    'type': "connect"
  }
  websocket.send(JSON.stringify(message));
}

document.addEventListener("DOMContentLoaded", function() {
  checkSupported();
  
  startButton.addEventListener('click', (event) => {
    start();
  })
  socketCloseListener();
  
  // websocket = new WebSocket("ws://localhost:6666");
  // websocket.addEventListener('open', () => {
  //   console.log('Connected to Server!')
  //   connect();
  // })
    // connect();
  // startGame();
});


function start() {
  message = {
    'type': 'start',
    'client_id': window.clientID,
    'data': {} // FIXME WYWAL?
  }
  websocket.send(JSON.stringify(message));
}

function max(a, b) {
  return a > b ? a : b;
}

function startGame() {

  window.gameIsOver = false;

  let mySnake = window.mySnake;
  let enemySnake = window.enemySnake;
  let food = window.food;

  // window.gridSize = 20;

  // mySnake = {'coordinates': [{'x': 20, 'y': 20}], 'direction': 'right', 'score': 0, 'grow': false};
  // enemySnake = {'coordinates': [{'x': 40, 'y': 80}], 'direction': 'left', 'score': 0, 'grow': false};
  // food = {'coordinates': {'x': 80, 'y': 80}, 'eaten': false};

  // window.mySnake = mySnake;
  // window.enemySnake = enemySnake;
  // window.food = food;
  // window.boardWidth = 600; //FIXME!!
  // window.boardHeight = 600; // FIXME!!

  ctx = window.ctx;
  ctx.clearRect(0,0, canvas.width, canvas.height);

  updateScores(mySnake, enemySnake);
  drawScene(mySnake, enemySnake, food, {});

  window.allowPressKeys = true;
  window.iteration = 1
  
  window.intervalID = setInterval(gameIteration, 1000);
  window.time = new Date(); 
}
   

function moveUp(snake) {
  coordinates = snake['coordinates'];
  movedHead = {...snake['coordinates'][0]};
  movedHead['y'] -= 1*gridSize;
  coordinates.unshift(movedHead);
  if (snake['grow']) {
    snake['grow'] = false;
  } else {
    coordinates.pop();
  }
  return snake;
}

function moveDown(snake){
  coordinates = snake['coordinates'];
  movedHead = {...snake['coordinates'][0]};
  movedHead['y'] += 1*gridSize;
  coordinates.unshift(movedHead)
  if (snake['grow']) {
    snake['grow'] = false;
  } else {
    coordinates.pop();
  }
  return snake;
}

function moveLeft(snake){
  coordinates = snake['coordinates'];
  movedHead = {...snake['coordinates'][0]};
  movedHead['x'] -= 1*gridSize;
  coordinates.unshift(movedHead);
  if (snake['grow']) {
    snake['grow'] = false;
  } else {
    coordinates.pop();
  }
  return snake;
}

function moveRight(snake) {
  coordinates = snake['coordinates'];
  movedHead = {...snake['coordinates'][0]};
  movedHead['x'] += 1*gridSize;
  coordinates.unshift(movedHead);
  if (snake['grow']) {
    snake['grow'] = false;
  } else {
    coordinates.pop();
  }
  return snake;
}

function changeDirection(snake, newDirection) {
  direction = snake['direction']
  if (direction == 'up' && newDirection != 'down') {
    direction = newDirection;
  } else if (direction == 'down' && newDirection != 'up') {
    direction = newDirection;
  } else if (direction == 'left' && newDirection != 'right') {
    direction = newDirection;
  } else if (direction == 'right' && newDirection != 'left') {
    direction = newDirection;
  } 
  snake['direction'] = direction

  return snake
}

function eatFood(mySnake, enemySnake, food) {
  let breakLoop = false;

  snakeArray = [mySnake, enemySnake]
  for (let i = 0; i < snakeArray.length; i++) {
    if (breakLoop) {
      break;
    }
    snake = snakeArray[i];
    for (let j = 0; j < snake['coordinates'].length; j++) {
      block = snake['coordinates'][j];
      if (food['coordinates']['x'] == block['x'] && food['coordinates']['y'] == block['y']) {
        snake['score'] += 1;
        snake['grow'] = true;
        food['eaten'] = true;
        breakLoop = true;
        break;
      }
    }
  }  
  return mySnake, enemySnake, food
}

//TODO: CZY JA MAM RUSZAC CZYIMS?
function moveDirection(mySnake, enemySnake) {
  
  // snakeArray = [mySnake] //, enemySnake]  // FIXME!!!!!!!!!!!!!!!!!!!!!!!!!!
  snakeArray = [mySnake, enemySnake]

  for (let i=0; i < snakeArray.length; i++) { 
    snake = snakeArray[i];
    snakeDirection = snake['direction']
    if (snakeDirection == 'right') {
      moveRight(snake)
    } else if (snakeDirection == 'left'){
      moveLeft(snake)
    } else if (snakeDirection == 'up'){
      moveUp(snake)
    } else if (snakeDirection == 'down'){
      moveDown(snake)
    }
  } 
  return mySnake, enemySnake
}


function checkCollisions(mySnake, enemySnake, boardWidth, boardHeight) {

  function outOfBounds(head, boardWidth, boardHeight) {
    if (head['x'] < 0 || head['x'] >= boardWidth || head['y'] < 0 || head['y'] >= boardHeight) {
      return true;
    }
    return false;
  }
  
  function checkCollision(coordinates_1, coordinates_2) {
    if (coordinates_1['x'] == coordinates_2['x'] && coordinates_1['y'] == coordinates_2['y']) {
      return true;
    }
    return false;
  }

  var myHead = mySnake['coordinates'][0];
  var enemyHead = enemySnake['coordinates'][0];
  
  var mySnakeDead = false;
  var enemySnakeDead = false;

  mySnakeDead = outOfBounds(myHead, boardWidth, boardHeight)
  enemySnakeDead = outOfBounds(enemyHead, boardWidth, boardHeight)

  // Check collision with self
  for (let i = 1; i < mySnake['coordinates'].length; i++) {
    if (checkCollision(myHead, mySnake['coordinates'][i]) == true) {
      mySnakeDead = true;
      mySnake['score'] = max(i, 0);
    } 
  }
  
  // Check collision with self - enemy
  for (let i = 1; i < enemySnake['coordinates'].length; i++) {
    if (checkCollision(enemyHead, enemySnake['coordinates'][i]) == true) {
      enemySnakeDead = true;
      enemySnake['score'] = max(i, 0);
    } 
  }

  // Check collision with other snake
  for (let i = 0; i < enemySnake['coordinates'].length; i++) {
    if (checkCollision(myHead, enemySnake['coordinates'][i]) == true) {
      mySnakeDead = true;
      mySnake['score'] = max(i, 0);
    } 
  }
  
  for (let i = 0; i < mySnake['coordinates'].length; i++) {
    if (checkCollision(enemyHead, mySnake['coordinates'][i]) == true) {
      enemySnakeDead = true;
      enemySnake['score'] = max(i, 0);
    } 
  }

  collisionStatus = {'me': mySnakeDead, 'enemy': enemySnakeDead};

  return collisionStatus;
}

  
function restart(){
  pause();
  start();
}
  
function pause() {
  clearInterval(window.intervalID);
  window.allowPressKeys = false;
}
  
function play() { //FIXME
  var interval = setInterval(drawScene, 100);
  window.allowPressKeys = true;
}
  
function drawX(x, y) {
  ctx.beginPath();

  ctx.moveTo(x, y);
  ctx.lineTo(x + gridSize, y+gridSize);

  ctx.moveTo(x + gridSize, y);
  ctx.lineTo(x, y + gridSize);
  ctx.stroke();
}

function drawScene(mySnake, enemySnake, food, collisionStatus) {

  ctx = window.ctx;
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  ctx.fillStyle = "rgb(204,204,0)";
  ctx.fillRect(mySnake['coordinates'][0]['x'], mySnake['coordinates'][0]['y'], gridSize, gridSize);
  for (let i=1; i < mySnake['coordinates'].length; i++) {
    ctx.fillStyle = `rgb(255,255,${i})`;
    block = mySnake['coordinates'][i];
    ctx.fillRect(block['x'], block['y'], gridSize, gridSize);
  }

  ctx.fillStyle = "rgb(0,204,204)";
  ctx.fillRect(enemySnake['coordinates'][0]['x'], enemySnake['coordinates'][0]['y'], gridSize, gridSize);
  for (let i=1; i < enemySnake['coordinates'].length; i++) {
    ctx.fillStyle = `rgb(${i}, 255,255)`;
    block = enemySnake['coordinates'][i];
    ctx.fillRect(block['x'], block['y'], gridSize, gridSize);
  }

  ctx.fillStyle = "rgb(255,0,0)";
  ctx.fillRect(food['coordinates']['x'], food['coordinates']['y'], gridSize, gridSize); 


  if (Object.keys(collisionStatus).length !== 0) {
    if (collisionStatus['me'] == true) {
      drawX(mySnake['coordinates'][0]['x'], mySnake['coordinates'][0]['y'])
    }
    if (collisionStatus['enemy'] == true) {
      drawX(enemySnake['coordinates'][0]['x'], enemySnake['coordinates'][0]['y'])
    }
  }

  // TODO: CZY RYSOWANIE  PUNKTOW TEZ TU GDZIES??
}
  

function gameOver(collistionStatus) {

  mySnakeDead = collistionStatus['me'];
  enemySnakeDead = collistionStatus['enemy'];

  pause();
  if (mySnakeDead && enemySnakeDead) {
    alert("Game Over. Your score was "); //fixme + score
  } else if (enemySnakeDead) {
    alert("You win!. Your score was ");
  } else if (mySnakeDead) {
    alert("You loose :<. Your score was ");
  }
  
  window.ctx.clearRect(0,0, canvas.width, canvas.height);
  // document.getElementById('play_menu').style.display='none'; //FIXME!!!
  // document.getElementById('restart_menu').style.display='block';
}
  
function updateScores(mySnake, enemySnake){
  let myScore = mySnake['score']
  let enemyScore = enemySnake['score']

  // document.getElementById('myScore').innerText = myScore; //FIXME
  // document.getElementById('enemyScore').innerText = enemyScore;
}
  
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


async function gameIteration() {


  if (!window.game_synchronized) {
    return;
  }
  window.game_synchronized = false;

  let mySnake = window.mySnake;
  let enemySnake = window.enemySnake;
  let food = window.food;
  let iteration = window.iteration;
  let boardWidth = window.boardWidth;
  let boardHeight = window.boardHeight;
  let time = window.time;

  let currentTime = new Date();
  let seconds = (currentTime.getTime() - time.getTime()) / 1000;
  let doLogic = true; // FIXME
  if (seconds > 0.1 && !window.gameIsOver) {
    window.time = new Date();
    doLogic = true;
  }
  
  let context = {}

  if (window.gameIsOver) {
    context = window.collisionStatus;
    drawScene(mySnake, enemySnake, food, context);
    // alert('game over!') // FIXME
    await sleep(100);
    gameOver(context); // FIXME TO JEST ZAPAMIETANE??
    doLogic = false;
  }

  if (doLogic){
    mySnake, enemySnake = moveDirection(mySnake, enemySnake);
  }

  drawScene(mySnake, enemySnake, food, context);

  if (doLogic) {
    let collisionStatus = checkCollisions(mySnake, enemySnake, boardWidth, boardHeight);

    mySnake, enemySnake, food = eatFood(mySnake, enemySnake, food);

    // if (food['eaten'] == true) {
    //   // TODO: notify server
    //   food['eaten'] = false
    //   food['coordinates'] = {'x': food['coordinates']['x']+1*gridSize, 'y': food['coordinates']['y']+1*gridSize} //FIXME
    // }

    updateScores(mySnake, enemySnake)

    if (collisionStatus['me'] == true || collisionStatus['enemy'] == true) {
      // TODO: END
      window.gameIsOver = true;
      window.collisionStatus = collisionStatus;
    }
  }

  window.mySnake = mySnake;
  window.enemySnake = enemySnake;
  window.food = food;
  window.iteration = iteration + 1;

  let taken_coordinates = []
  // TODO CZY TO POTRZEBNE
  if (food['eaten'] == true) {
    taken_coordinates = [mySnake['coordinates'], enemySnake['coordinates']];
    food['eaten'] = false
  }

  message = {
    'type': 'game_iter',
    'client_id': clientID,
    'data': {'iteration': window.iteration, 'my_snake_direction': window.mySnake['direction'], 'food_eaten': window.food['eaten'], 'taken_coordinates': taken_coordinates}
    // 'data': {'iteration': iteration, 'mySnakeDirection': mySnake['direction'], 'food_eaten': food['eaten']}
  }

  websocket.send((JSON.stringify(message)));
}


// SET KEYSTROKES
document.onkeydown = function(event) {

  if (!window.allowPressKeys){
    return null;
  }

  var keyCode; 
  
  if(event == null) {
    keyCode = window.event.code; 
  } else {
    keyCode = event.code; 
  }
  
  switch(keyCode) {
    case 'ArrowLeft':
        changeDirection(mySnake, 'left');
        break; 
    case 'ArrowUp':
        changeDirection(mySnake, 'up');
        break; 
    case 'ArrowRight':
        changeDirection(mySnake, 'right');
        break; 
    case 'ArrowDown':
        changeDirection(mySnake, 'down');
        break; 
    // case 'keyA':
    //     changeDirection(window.enemySnake, 'left');
    //     break; 
    // case 'keyW':
    //     changeDirection(window.enemySnake, 'up');
    //     break; 
    // case 'keyD':
    //     changeDirection(window.enemySnake, 'right');
    //     break; 
    // case 'keyS':
    //     changeDirection(window.enemySnake, 'down');
    //     break; 
    default: 
        break; 
  } 
}
  
