import pygame
from game import Game

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Borko - Poker Card Game")

# Main game loop
def main():
    game = Game()
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    game.handle_click(event)

        game.draw(screen)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
