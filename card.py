import pygame
import os

# Constants (shared across modules)
CARD_WIDTH = 100
CARD_HEIGHT = 140
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Card class - represents a single playing card
class Card:
    def __init__(self, suit, value):
        self.suit = suit  # e.g., 'hearts', 'diamonds', 'clubs', 'spades'
        self.value = value  # 1-13 (Ace to King)
        self.chip_value = self.get_chip_value()  # Chip value based on rank
        self.image = None
        self.load_image()

    def get_chip_value(self):
        # Define chip values for each rank
        if self.value == 1:  # Ace
            return 11
        elif self.value >= 11:  # Jack, Queen, King
            return 10
        else:
            return self.value  # 2-10

    def load_image(self):
        # Load card image from assets
        image_path = f"assets/Playing Cards/card-{self.suit}-{self.value}.png"
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
        else:
            # Fallback: create a colored rectangle if image not found
            self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.image.fill(WHITE)

    def draw(self, screen, x, y, selected=False):
        if selected:
            y -= 20  # Shift up to indicate selection
        screen.blit(self.image, (x, y))

# Deck class - represents a deck of cards using a list (dynamic array)
class Deck:
    def __init__(self):
        self.cards = []  # List to store Card objects
        self.create_deck()

    def create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        for suit in suits:
            for value in range(1, 14):  # 1=Ace, 11=Jack, 12=Queen, 13=King
                self.cards.append(Card(suit, value))

    def shuffle(self):
        import random
        random.shuffle(self.cards)  # Shuffle the list in place

    def draw_card(self):
        if self.cards:
            return self.cards.pop()  # Remove and return the last card
        return None