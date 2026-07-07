"""Number Guessing Game — Pygame Edition."""

import sys
import random
import pygame

W, H = 520, 680
FPS = 60
MAX_TRIES = 7
LOW, HIGH = 1, 100

BG = (26, 27, 38)
CARD = (32, 34, 47)
ACCENT = (122, 162, 247)
GOOD = (158, 206, 106)
BAD = (247, 118, 142)
GOLD = (224, 175, 104)
TEXT = (192, 202, 245)
MUTED = (86, 95, 137)
INPUT_BG = (36, 40, 59)


class Game:
    """Mutable game state for one round."""

    def __init__(self):
        self.secret = random.randint(LOW, HIGH)
        self.tries_left = MAX_TRIES
        self.history: list[tuple[int, str]] = []
        self.state = "playing"

    def guess(self, value: int):
        if self.state != "playing":
            return
        if value < self.secret:
            hint = "Too Low"
        elif value > self.secret:
            hint = "Too High"
        else:
            hint = "Correct!"
        self.history.append((value, hint))
        self.tries_left -= 1
        if value == self.secret:
            self.state = "won"
        elif self.tries_left == 0:
            self.state = "lost"


def draw_card(surf, color, box, radius=12):
    pygame.draw.rect(surf, color, box, border_radius=radius)


def draw_text(surf, msg, font, color, x, y, anchor="center"):
    img = font.render(msg, True, color)
    surf.blit(img, img.get_rect(**{anchor: (x, y)}))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Number Guessing Game")
    clock = pygame.time.Clock()

    f_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
    f_sub = pygame.font.SysFont("Segoe UI", 18)
    f_label = pygame.font.SysFont("Consolas", 20, bold=True)
    f_small = pygame.font.SysFont("Consolas", 20)
    f_huge = pygame.font.SysFont("Segoe UI", 64, bold=True)
    f_btn = pygame.font.SysFont("Segoe UI", 18, bold=True)

    input_box = pygame.Rect(W // 2 - 120, 260, 240, 52)
    guess_btn = pygame.Rect(W // 2 - 80, 328, 160, 46)
    new_btn = pygame.Rect(W // 2 - 80, H - 72, 160, 44)

    game = Game()
    input_text = ""
    error_msg = ""

    def submit():
        nonlocal input_text
        if input_text.isdigit() and LOW <= int(input_text) <= HIGH:
            game.guess(int(input_text))
            input_text = ""
            return True
        return False

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game.state == "playing":
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        error_msg = ""
                    elif event.key == pygame.K_RETURN:
                        error_msg = "" if submit() else f"Enter a number {LOW}-{HIGH}"
                    elif event.unicode.isdigit() and len(input_text) < 3:
                        input_text += event.unicode
                        error_msg = ""

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if guess_btn.collidepoint(mx, my) and game.state == "playing":
                    error_msg = "" if submit() else f"Enter a number {LOW}-{HIGH}"
                elif new_btn.collidepoint(mx, my):
                    game, input_text, error_msg = Game(), "", ""

        screen.fill(BG)

        draw_card(screen, CARD, (20, 16, W - 40, 130))
        draw_text(screen, "Number Guessing Game", f_title, ACCENT, W // 2, 56)
        draw_text(screen, f"Guess a number between {LOW} and {HIGH}", f_sub, MUTED, W // 2, 94)
        draw_text(screen, f"Tries left: {game.tries_left} / {MAX_TRIES}", f_label,
                  GOLD if game.tries_left > 2 else BAD, W // 2, 124)

        if game.state == "playing":
            draw_card(screen, INPUT_BG, input_box, 10)
            pygame.draw.rect(screen, ACCENT, input_box, 2, border_radius=10)
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            draw_text(screen, input_text + cursor, f_small, TEXT,
                      input_box.centerx, input_box.centery)

            hover = guess_btn.collidepoint(mx, my)
            draw_card(screen, ACCENT if hover else (58, 121, 168), guess_btn, 10)
            draw_text(screen, "GUESS", f_btn, BG, guess_btn.centerx, guess_btn.centery)

            if error_msg:
                draw_text(screen, error_msg, f_small, BAD, W // 2, 388)

        elif game.state == "won":
            draw_card(screen, (32, 62, 45), (40, 200, W - 80, 100), 14)
            draw_text(screen, "You Won!", f_title, GOOD, W // 2, 235)
            draw_text(screen, f"The number was {game.secret}", f_sub, TEXT, W // 2, 272)

        elif game.state == "lost":
            draw_card(screen, (62, 32, 40), (40, 200, W - 80, 100), 14)
            draw_text(screen, "Game Over", f_title, BAD, W // 2, 235)
            draw_text(screen, f"The number was {game.secret}", f_sub, TEXT, W // 2, 272)

        if game.history:
            draw_card(screen, CARD, (20, 400, W - 40, H - 490), 12)
            draw_text(screen, "History", f_label, MUTED, W // 2, 418)
            for i, (guess, hint) in enumerate(reversed(game.history[-5:])):
                color = GOOD if hint == "Correct!" else TEXT
                draw_text(screen, f"  {guess:>3}  ->  {hint}", f_small, color,
                          W // 2 - 100, 448 + i * 28, "midleft")

        new_hover = new_btn.collidepoint(mx, my)
        draw_card(screen, BAD if new_hover else (140, 60, 75), new_btn, 10)
        draw_text(screen, "New Game", f_btn, TEXT, new_btn.centerx, new_btn.centery)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
