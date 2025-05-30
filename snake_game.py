from browser import document, html, window, timer
import random

# Game constants
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
GRID_SIZE = 20  # Size of each snake segment and food item
GRID_WIDTH = CANVAS_WIDTH // GRID_SIZE
GRID_HEIGHT = CANVAS_HEIGHT // GRID_SIZE

# Colors
SNAKE_COLOR = "green"
FOOD_COLOR = "red"
BACKGROUND_COLOR = "#FFFFFF" # White background for canvas

# Game state
snake = []
snake_direction = "RIGHT"  # Initial direction
food = None
score = 0
game_over = False
game_loop_id = None # To store the timer ID for stopping the game loop

# High score handling
today_str = window.Date.new().toLocaleDateString()
HIGH_SCORE_KEY = f"snake_high_score_{today_str}"

canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")

score_display = document["current-score"]
highest_score_display = document["highest-score"]
game_over_message = document["game-over-message"]
restart_button = document["restart-button"]

def get_highest_score():
    """Retrieves the highest score for today from localStorage."""
    hs = window.localStorage.getItem(HIGH_SCORE_KEY)
    return int(hs) if hs else 0

def set_highest_score(new_score):
    """Sets the highest score for today in localStorage."""
    window.localStorage.setItem(HIGH_SCORE_KEY, str(new_score))
    highest_score_display.text = str(new_score)

def init_game():
    """Initializes or resets the game state."""
    global snake, snake_direction, food, score, game_over, game_loop_id

    if game_loop_id is not None:
        timer.cancel(game_loop_id) # Clear previous game loop if any

    snake = [
        {"x": GRID_WIDTH // 2, "y": GRID_HEIGHT // 2},
        {"x": GRID_WIDTH // 2 - 1, "y": GRID_HEIGHT // 2},
        {"x": GRID_WIDTH // 2 - 2, "y": GRID_HEIGHT // 2},
    ]
    snake_direction = "RIGHT"
    place_food()
    score = 0
    game_over = False

    score_display.text = str(score)
    highest_score_display.text = str(get_highest_score())
    game_over_message.style.display = "none"
    restart_button.style.display = "none"
    canvas.style.opacity = "1"


    game_loop_id = timer.set_interval(game_loop, 130) # Start the game loop (adjust speed here)

def place_food():
    """Places food at a random position on the grid."""
    global food
    while True:
        food = {"x": random.randint(0, GRID_WIDTH - 1), "y": random.randint(0, GRID_HEIGHT - 1)}
        # Ensure food doesn't spawn on the snake
        if not any(segment["x"] == food["x"] and segment["y"] == food["y"] for segment in snake):
            break

def draw_rect(x, y, color):
    """Draws a rectangle on the canvas."""
    ctx.fillStyle = color
    ctx.fillRect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    ctx.strokeStyle = BACKGROUND_COLOR # For a little border effect within segments
    ctx.strokeRect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)


def draw_game():
    """Draws the game elements (snake, food) on the canvas."""
    # Clear canvas
    ctx.fillStyle = BACKGROUND_COLOR
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    # Draw snake
    for segment in snake:
        draw_rect(segment["x"], segment["y"], SNAKE_COLOR)

    # Draw food
    if food:
        draw_rect(food["x"], food["y"], FOOD_COLOR)

def move_snake():
    """Moves the snake according to its current direction."""
    global snake, snake_direction, game_over, score

    if game_over:
        return

    head = {"x": snake[0]["x"], "y": snake[0]["y"]}

    if snake_direction == "UP":
        head["y"] -= 1
    elif snake_direction == "DOWN":
        head["y"] += 1
    elif snake_direction == "LEFT":
        head["x"] -= 1
    elif snake_direction == "RIGHT":
        head["x"] += 1

    # Check for collision with walls
    if head["x"] < 0 or head["x"] >= GRID_WIDTH or \
       head["y"] < 0 or head["y"] >= GRID_HEIGHT:
        end_game()
        return

    # Check for collision with self
    for segment in snake[1:]: # Check against the body, not the current head
        if head["x"] == segment["x"] and head["y"] == segment["y"]:
            end_game()
            return

    snake.insert(0, head) # Add new head

    # Check for food consumption
    if food and head["x"] == food["x"] and head["y"] == food["y"]:
        score += 10
        score_display.text = str(score)
        place_food()
        # Update highest score if current score is greater
        if score > get_highest_score():
            set_highest_score(score)
    else:
        snake.pop() # Remove tail if no food eaten

def handle_keydown(event):
    """Handles keyboard input for changing snake direction."""
    global snake_direction
    # Prevent snake from immediately reversing
    if event.key == "ArrowUp" and snake_direction != "DOWN":
        snake_direction = "UP"
    elif event.key == "ArrowDown" and snake_direction != "UP":
        snake_direction = "DOWN"
    elif event.key == "ArrowLeft" and snake_direction != "RIGHT":
        snake_direction = "LEFT"
    elif event.key == "ArrowRight" and snake_direction != "LEFT":
        snake_direction = "RIGHT"

def end_game():
    """Handles the game over state."""
    global game_over, game_loop_id
    game_over = True
    if game_loop_id is not None:
        timer.cancel(game_loop_id)
    game_over_message.style.display = "block"
    restart_button.style.display = "block"
    canvas.style.opacity = "0.7" # Slightly fade out canvas

    # Ensure highest score is up-to-date one last time
    if score > get_highest_score():
        set_highest_score(score)


def game_loop():
    """The main game loop."""
    if not game_over:
        move_snake()
        draw_game()

# Event listeners
document.bind("keydown", handle_keydown)
restart_button.bind("click", lambda ev: init_game())

# Start the game
init_game()