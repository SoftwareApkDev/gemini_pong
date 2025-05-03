import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
WALL_THICKNESS = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Speeds
PLAYER_PADDLE_SPEED = 8
AI_PADDLE_SPEED = 6 # AI is slightly slower than player
BALL_INITIAL_SPEED_X = 7
BALL_INITIAL_SPEED_Y = 7

# --- Classes ---

class Paddle(pygame.Rect):
    """Represents a paddle in the game."""
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y, width, height)
        self.speed = speed

    def move(self, dy):
        """Moves the paddle vertically, clamping to screen bounds."""
        self.y += dy * self.speed
        # Clamp to screen bounds
        if self.top < WALL_THICKNESS:
            self.top = WALL_THICKNESS
        if self.bottom > SCREEN_HEIGHT - WALL_THICKNESS:
            self.bottom = SCREEN_HEIGHT - WALL_THICKNESS

    def draw(self, screen):
        """Draws the paddle on the screen."""
        pygame.draw.rect(screen, WHITE, self)

class Ball(pygame.Rect):
    """Represents the ball in the game."""
    def __init__(self, x, y, size, speed_x, speed_y):
        super().__init__(x, y, size, size)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.initial_pos = (x, y) # Store initial position for resetting

    def move(self):
        """Moves the ball based on its current speed."""
        self.x += self.speed_x
        self.y += self.speed_y

    def reset(self):
        """Resets the ball to the center with a random horizontal direction."""
        self.center = self.initial_pos
        # Randomize initial horizontal direction
        self.speed_x *= random.choice([-1, 1])
        # Randomize initial vertical direction slightly
        self.speed_y *= random.choice([-1, 1])
        # Ensure minimum vertical speed to avoid flat trajectories
        if abs(self.speed_y) < 3:
             self.speed_y = 3 * (1 if self.speed_y > 0 else -1)


    def draw(self, screen):
        """Draws the ball on the screen."""
        # Draw as a circle for better visual
        pygame.draw.ellipse(screen, WHITE, self)

# --- AI Logic ---

def ai_movement(ball, paddle):
    """Controls the AI paddle's movement."""
    # Simple AI: Move towards the ball's y-coordinate if it's on the AI's side
    if ball.centerx > SCREEN_WIDTH / 2: # Only track the ball when it's on the AI's side
        if paddle.centery < ball.centery:
            paddle.move(1) # Move down
        elif paddle.centery > ball.centery:
            paddle.move(-1) # Move up
        # Add a small dead zone or probability to make it less perfect
        # (Optional improvement)

# --- Game Setup ---

def setup_game():
    """Initializes Pygame, creates game objects, and returns them."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Pong")

    # Walls (optional, but visually separates top/bottom)
    top_wall = pygame.Rect(0, 0, SCREEN_WIDTH, WALL_THICKNESS)
    bottom_wall = pygame.Rect(0, SCREEN_HEIGHT - WALL_THICKNESS, SCREEN_WIDTH, WALL_THICKNESS)

    player_paddle = Paddle(
        WALL_THICKNESS + 10,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, PLAYER_PADDLE_SPEED
    )

    ai_paddle = Paddle(
        SCREEN_WIDTH - PADDLE_WIDTH - WALL_THICKNESS - 10,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, AI_PADDLE_SPEED
    )

    ball = Ball(
        SCREEN_WIDTH // 2 - BALL_SIZE // 2,
        SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
        BALL_SIZE,
        BALL_INITIAL_SPEED_X * random.choice([-1, 1]), # Start in a random horizontal direction
        BALL_INITIAL_SPEED_Y * random.choice([-1, 1])  # Start in a random vertical direction
    )

    # Score variables
    player_score = 0
    ai_score = 0
    font = pygame.font.Font(None, 74) # Font for displaying score

    clock = pygame.time.Clock()

    return screen, top_wall, bottom_wall, player_paddle, ai_paddle, ball, player_score, ai_score, font, clock

# --- Main Game Loop ---

def run_game():
    """Runs the main game loop."""
    screen, top_wall, bottom_wall, player_paddle, ai_paddle, ball, player_score, ai_score, font, clock = setup_game()

    running = True
    player_move_direction = 0 # -1 for up, 1 for down, 0 for stationary

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player_move_direction = -1
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    player_move_direction = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if player_move_direction == -1: # Stop moving only if that direction key was released
                         player_move_direction = 0
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if player_move_direction == 1: # Stop moving only if that direction key was released
                        player_move_direction = 0

        # --- Game Logic Updates ---
        player_paddle.move(player_move_direction)
        ai_movement(ball, ai_paddle) # AI controls its paddle

        ball.move()

        # Ball collision with top/bottom walls
        if ball.top <= top_wall.bottom or ball.bottom >= bottom_wall.top:
            ball.speed_y *= -1 # Reverse vertical direction

        # Ball collision with paddles
        # Check collision only if the ball is moving towards the paddle
        if ball.colliderect(player_paddle) and ball.speed_x < 0:
            ball.speed_x *= -1 # Reverse horizontal direction
            # Optional: Adjust vertical speed based on where the ball hit the paddle
            # center_dist = ball.centery - player_paddle.centery
            # ball.speed_y = center_dist * 0.2 # Example adjustment
            # Add a slight speed increase after hitting a paddle
            ball.speed_x *= 1.05
            ball.speed_y *= 1.05
            # Clamp maximum speed to prevent it from getting too fast
            max_speed = 15
            ball.speed_x = max(min(ball.speed_x, max_speed), -max_speed)
            ball.speed_y = max(min(ball.speed_y, max_speed), -max_speed)


        if ball.colliderect(ai_paddle) and ball.speed_x > 0:
            ball.speed_x *= -1 # Reverse horizontal direction
            # Optional: Adjust vertical speed
            # center_dist = ball.centery - ai_paddle.centery
            # ball.speed_y = center_dist * 0.2
            # Add a slight speed increase
            ball.speed_x *= 1.05
            ball.speed_y *= 1.05
            # Clamp maximum speed
            max_speed = 15
            ball.speed_x = max(min(ball.speed_x, max_speed), -max_speed)
            ball.speed_y = max(min(ball.speed_y, max_speed), -max_speed)

        # Scoring
        if ball.left <= 0: # Ball goes past player's paddle
            ai_score += 1
            ball.reset()
            # Reset ball speed after scoring
            ball.speed_x = BALL_INITIAL_SPEED_X * random.choice([-1, 1])
            ball.speed_y = BALL_INITIAL_SPEED_Y * random.choice([-1, 1])

        if ball.right >= SCREEN_WIDTH: # Ball goes past AI's paddle
            player_score += 1
            ball.reset()
            # Reset ball speed after scoring
            ball.speed_x = BALL_INITIAL_SPEED_X * random.choice([-1, 1])
            ball.speed_y = BALL_INITIAL_SPEED_Y * random.choice([-1, 1])

        # --- Drawing ---
        screen.fill(BLACK) # Clear screen

        # Draw walls
        pygame.draw.rect(screen, WHITE, top_wall)
        pygame.draw.rect(screen, WHITE, bottom_wall)

        # Draw center line (optional)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, WALL_THICKNESS), (SCREEN_WIDTH // 2, SCREEN_HEIGHT - WALL_THICKNESS))

        # Draw paddles and ball
        player_paddle.draw(screen)
        ai_paddle.draw(screen)
        ball.draw(screen)

        # Draw scores
        player_score_text = font.render(str(player_score), True, WHITE)
        ai_score_text = font.render(str(ai_score), True, WHITE)
        screen.blit(player_score_text, (SCREEN_WIDTH // 4, WALL_THICKNESS + 20))
        screen.blit(ai_score_text, (SCREEN_WIDTH * 3 // 4 - ai_score_text.get_width(), WALL_THICKNESS + 20))


        # --- Update Display ---
        pygame.display.flip() # Or pygame.display.update()

        # --- Frame Rate Control ---
        clock.tick(60) # Limit to 60 frames per second

    # --- Quit Pygame ---
    pygame.quit()
    sys.exit()

# --- Run the game ---
if __name__ == "__main__":
    run_game()