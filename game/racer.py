import pygame

from persistence import (
    CAR_COLORS,
    DIFFICULTY_CONFIG,
    load_leaderboard,
    load_settings,
    save_settings,
)
from racer import RacerGame, WIDTH, HEIGHT, FPS
from ui import Button, WHITE, BLACK, GRAY, DARK, YELLOW, GREEN, RED, BLUE, draw_text, draw_panel

pygame.init()
pygame.display.set_caption("TSIS 3 Racer Game")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 26)
big_font = pygame.font.SysFont("Arial", 52, bold=True)
small_font = pygame.font.SysFont("Arial", 20)

settings = load_settings()
username = "Player"
last_result = None


def make_button(text, x, y, w=260, h=56):
    return Button(pygame.Rect(x, y, w, h), text, font)


def ask_username() -> str:
    global username
    text = username if username != "Player" else ""
    active = True
    while active:
        screen.fill(DARK)
        draw_text(screen, "Enter username", big_font, WHITE, WIDTH // 2, 210, center=True)
        draw_text(screen, "Press Enter to start", small_font, WHITE, WIDTH // 2, 270, center=True)
        box = pygame.Rect(WIDTH // 2 - 180, 330, 360, 56)
        pygame.draw.rect(screen, BLACK, box, border_radius=10)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=10)
        draw_text(screen, text or "Player", font, WHITE if text else GRAY, box.x + 18, box.y + 13)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    username = text.strip() or "Player"
                    return username
                if event.key == pygame.K_ESCAPE:
                    return "back"
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 16 and event.unicode.isprintable():
                    text += event.unicode

        pygame.display.flip()
        clock.tick(FPS)


def main_menu() -> str:
    play = make_button("Play", WIDTH // 2 - 130, 260)
    leaderboard = make_button("Leaderboard", WIDTH // 2 - 130, 335)
    settings_btn = make_button("Settings", WIDTH // 2 - 130, 410)
    quit_btn = make_button("Quit", WIDTH // 2 - 130, 485)
    buttons = [play, leaderboard, settings_btn, quit_btn]

    while True:
        screen.fill(DARK)
        draw_text(screen, "RACER GAME", big_font, YELLOW, WIDTH // 2, 150, center=True)
        draw_text(screen, "TSIS 3 — Advanced Driving, Leaderboard & Power-Ups", small_font, WHITE, WIDTH // 2, 205, center=True)

        for button in buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if play.clicked(event):
                result = ask_username()
                if result == "quit":
                    return "quit"
                if result != "back":
                    return "play"
            if leaderboard.clicked(event):
                return "leaderboard"
            if settings_btn.clicked(event):
                return "settings"
            if quit_btn.clicked(event):
                return "quit"

        pygame.display.flip()
        clock.tick(FPS)


def leaderboard_screen() -> str:
    back = make_button("Back", WIDTH // 2 - 130, HEIGHT - 90)
    while True:
        screen.fill(DARK)
        draw_text(screen, "TOP 10 LEADERBOARD", big_font, YELLOW, WIDTH // 2, 70, center=True)
        entries = load_leaderboard()
        y = 150
        headers = "Rank   Name             Score     Distance"
        draw_text(screen, headers, small_font, WHITE, 105, 120)
        for index, entry in enumerate(entries[:10], start=1):
            line = f"{index:<6} {entry.get('name', 'Player')[:14]:<16} {entry.get('score', 0):<9} {entry.get('distance', 0)} m"
            draw_text(screen, line, small_font, WHITE, 105, y)
            y += 42
        if not entries:
            draw_text(screen, "No scores yet. Play first!", font, WHITE, WIDTH // 2, 220, center=True)
        back.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if back.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "menu"

        pygame.display.flip()
        clock.tick(FPS)


def settings_screen() -> str:
    global settings
    sound_btn = make_button("", WIDTH // 2 - 160, 210, 320)
    color_btn = make_button("", WIDTH // 2 - 160, 290, 320)
    difficulty_btn = make_button("", WIDTH // 2 - 160, 370, 320)
    back = make_button("Back", WIDTH // 2 - 130, 530)

    color_names = list(CAR_COLORS.keys())
    difficulty_names = list(DIFFICULTY_CONFIG.keys())

    while True:
        sound_btn.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        color_btn.text = f"Car color: {settings['car_color']}"
        difficulty_btn.text = f"Difficulty: {settings['difficulty']}"

        screen.fill(DARK)
        draw_text(screen, "SETTINGS", big_font, YELLOW, WIDTH // 2, 120, center=True)
        draw_text(screen, "Changes are saved to settings.json", small_font, WHITE, WIDTH // 2, 170, center=True)

        for btn in [sound_btn, color_btn, difficulty_btn, back]:
            btn.draw(screen)

        preview = pygame.Rect(WIDTH // 2 - 24, 455, 48, 78)
        pygame.draw.rect(screen, tuple(CAR_COLORS[settings["car_color"]]), preview, border_radius=10)
        pygame.draw.rect(screen, WHITE, preview, 2, border_radius=10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if sound_btn.clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)
            if color_btn.clicked(event):
                current = color_names.index(settings["car_color"])
                settings["car_color"] = color_names[(current + 1) % len(color_names)]
                save_settings(settings)
            if difficulty_btn.clicked(event):
                current = difficulty_names.index(settings["difficulty"])
                settings["difficulty"] = difficulty_names[(current + 1) % len(difficulty_names)]
                save_settings(settings)
            if back.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "menu"

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(result_text="Game Over") -> str:
    retry = make_button("Retry", WIDTH // 2 - 130, 410)
    menu = make_button("Main Menu", WIDTH // 2 - 130, 485)
    leaderboard = make_button("Leaderboard", WIDTH // 2 - 130, 560)

    entries = load_leaderboard()
    latest = entries[0] if entries else {"score": 0, "distance": 0, "coins": 0, "name": username}

    while True:
        screen.fill(DARK)
        draw_text(screen, result_text, big_font, RED if result_text == "Game Over" else GREEN, WIDTH // 2, 120, center=True)
        draw_panel(screen, pygame.Rect(WIDTH // 2 - 180, 190, 360, 170))
        draw_text(screen, f"Name: {username}", font, WHITE, WIDTH // 2, 215, center=True)
        draw_text(screen, f"Score: {latest.get('score', 0)}", font, YELLOW, WIDTH // 2, 255, center=True)
        draw_text(screen, f"Distance: {latest.get('distance', 0)} m", font, WHITE, WIDTH // 2, 295, center=True)
        draw_text(screen, f"Coins: {latest.get('coins', 0)}", font, WHITE, WIDTH // 2, 335, center=True)

        for button in [retry, menu, leaderboard]:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retry.clicked(event):
                return "play"
            if menu.clicked(event):
                return "menu"
            if leaderboard.clicked(event):
                return "leaderboard"

        pygame.display.flip()
        clock.tick(FPS)


def main() -> None:
    state = "menu"
    while state != "quit":
        if state == "menu":
            state = main_menu()
        elif state == "leaderboard":
            state = leaderboard_screen()
        elif state == "settings":
            state = settings_screen()
        elif state == "play":
            game = RacerGame(screen, username, settings)
            next_state = game.run()
            if next_state == "quit":
                state = "quit"
            else:
                state = game_over_screen("Finished!" if game.finished else "Game Over")
        else:
            state = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()
