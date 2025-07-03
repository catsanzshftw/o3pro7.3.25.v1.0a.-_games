import sys
import math
import random
import array
import pygame

# ---------- Constants ----------
WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15

PADDLE_SPEED = 6
AI_SPEED = 5
BALL_SPEED = 5
WIN_SCORE = 5

# ---------- Helpers ----------
def make_beep(freq=440, duration=0.05, volume=0.5, sample_rate=44100):
    """Generate a short sine‑wave beep as a pygame Sound (no external assets)."""
    n_samples = int(sample_rate * duration)
    buf = array.array("h")
    amplitude = int(volume * 32767)
    for i in range(n_samples):
        t = i / sample_rate
        buf.append(int(amplitude * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=buf.tobytes())

def reset_positions(ball, player, ai, ball_vel):
    """Center everything and launch the ball in a random direction."""
    ball.center = (WIDTH // 2, HEIGHT // 2)
    player.centery = HEIGHT // 2
    ai.centery = HEIGHT // 2
    ball_vel.update(random.choice((-1, 1)) * BALL_SPEED,
                    random.choice((-1, 1)) * BALL_SPEED)

# ---------- Main ----------
def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 48)
    big_font = pygame.font.SysFont(None, 72)
    beep = make_beep()

    # Game objects
    player = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                         PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(WIDTH - 30, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                     PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2,
                       HEIGHT // 2 - BALL_SIZE // 2,
                       BALL_SIZE, BALL_SIZE)
    ball_vel = pygame.Vector2(BALL_SPEED, BALL_SPEED)

    player_score = ai_score = 0
    game_over = False
    reset_positions(ball, player, ai, ball_vel)

    running = True
    while running:
        # ----- Event Handling -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_over and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN):
                    player_score = ai_score = 0
                    game_over = False
                    reset_positions(ball, player, ai, ball_vel)
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    running = False

        keys = pygame.key.get_pressed()
        if not game_over:
            # ----- Player Movement -----
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player.y -= PADDLE_SPEED
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player.y += PADDLE_SPEED
            player.y = max(0, min(HEIGHT - PADDLE_HEIGHT, player.y))

            # ----- AI Movement -----
            if ai.centery < ball.centery - 10:
                ai.y += AI_SPEED
            elif ai.centery > ball.centery + 10:
                ai.y -= AI_SPEED
            ai.y = max(0, min(HEIGHT - PADDLE_HEIGHT, ai.y))

            # ----- Ball Movement -----
            ball.x += int(ball_vel.x)
            ball.y += int(ball_vel.y)

            # Wall collisions
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_vel.y *= -1
                beep.play()

            # Paddle collisions
            if ball.colliderect(player) and ball_vel.x < 0:
                ball.left = player.right
                ball_vel.x *= -1
                beep.play()
            if ball.colliderect(ai) and ball_vel.x > 0:
                ball.right = ai.left
                ball_vel.x *= -1
                beep.play()

            # Scoring
            if ball.left <= 0:
                ai_score += 1
                beep.play()
                reset_positions(ball, player, ai, ball_vel)
            elif ball.right >= WIDTH:
                player_score += 1
                beep.play()
                reset_positions(ball, player, ai, ball_vel)

            # Win condition
            if player_score == WIN_SCORE or ai_score == WIN_SCORE:
                game_over = True

        # ----- Drawing -----
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), player)
        pygame.draw.rect(screen, (255, 255, 255), ai)
        pygame.draw.ellipse(screen, (255, 255, 255), ball)
        pygame.draw.aaline(screen, (255, 255, 255),
                           (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        score_text = font.render(f"{player_score}   {ai_score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        if game_over:
            over_text = big_font.render("GAME OVER", True, (255, 0, 0))
            prompt_text = font.render("Restart? (Y/N)", True, (255, 255, 255))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2,
                                    HEIGHT // 2 - 60))
            screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2,
                                      HEIGHT // 2 + 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
