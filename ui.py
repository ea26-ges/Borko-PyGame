import pygame
import random

# UI Constants
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Button class - for user interaction
class Button:
    def __init__(self, x, y, width, height, text, color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# UI Manager class - handles all UI rendering and input
class UIManager:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

    def draw_text(self, screen, text, x, y, font=None, color=BLACK):
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        screen.blit(surface, (x, y))

    def draw_score_info(self, screen, current_score, target_score, round_num, turns_left, discards_left):
        self.draw_text(screen, f"Score: {current_score} / {target_score}", 10, 10)
        self.draw_text(screen, f"Round: {round_num}", 10, 40, self.small_font)
        self.draw_text(screen, f"Turns Left: {turns_left}", 10, 60, self.small_font)
        self.draw_text(screen, f"Discards Left: {discards_left}", 10, 80, self.small_font)

    def draw_hand(self, screen, hand, selected_indices):
        # Sort hand by rank for display (Ace low for sorting)
        sorted_hand = sorted(hand, key=lambda c: c.value)

        # Calculate centered position for hand
        total_hand_width = len(sorted_hand) * 100 + (len(sorted_hand) - 1) * 10  # CARD_WIDTH = 100
        start_x = (SCREEN_WIDTH - total_hand_width) // 2
        y = SCREEN_HEIGHT - 250  # Position higher above buttons

        # Draw hand
        for i, card in enumerate(sorted_hand):
            x = start_x + i * (100 + 10)  # CARD_WIDTH + 10
            # Check if this card is selected (find original index)
            orig_index = hand.index(card)
            selected = orig_index in selected_indices
            card.draw(screen, x, y, selected)

    def draw_jokers(self, screen, jokers):
        if jokers:
            joker_y = 50
            total_joker_width = len(jokers) * 100 + (len(jokers) - 1) * 10  # CARD_WIDTH = 100
            joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
            for i, joker in enumerate(jokers):
                x = joker_start_x + i * (100 + 10)  # CARD_WIDTH + 10
                joker.draw(screen, x, joker_y)

    def draw_joker_selection(self, screen, joker_options):
        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # Draw joker options
        joker_y = 300
        total_joker_width = len(joker_options) * 100 + (len(joker_options) - 1) * 10  # CARD_WIDTH = 100
        joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
        for i, joker in enumerate(joker_options):
            x = joker_start_x + i * (100 + 10)  # CARD_WIDTH + 10
            joker.draw(screen, x, joker_y)

            # Draw description below each joker
            desc_surface = self.tiny_font.render(joker.description, True, WHITE)
            desc_rect = desc_surface.get_rect(center=(x + 50, joker_y + 140 + 30))  # CARD_WIDTH//2, CARD_HEIGHT + 30
            screen.blit(desc_surface, desc_rect)

        # Draw selection prompt
        prompt_text = "Choose a Joker!"
        prompt_surface = self.font.render(prompt_text, True, WHITE)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(prompt_surface, prompt_rect)

    def get_hand_click_position(self, pos, hand):
        # Sort hand by rank for click detection (Ace low for sorting)
        sorted_hand = sorted(hand, key=lambda c: c.value)

        # Calculate centered position for hand
        total_hand_width = len(sorted_hand) * 100 + (len(sorted_hand) - 1) * 10  # CARD_WIDTH = 100
        start_x = (SCREEN_WIDTH - total_hand_width) // 2
        y = SCREEN_HEIGHT - 250  # Position higher above buttons

        # Check card clicks
        for i, card in enumerate(sorted_hand):
            x = start_x + i * (100 + 10)  # CARD_WIDTH + 10
            card_rect = pygame.Rect(x, y, 100, 140)  # CARD_WIDTH, CARD_HEIGHT
            if card_rect.collidepoint(pos):
                # Find original index in unsorted hand
                orig_index = hand.index(card)
                return orig_index
        return None

    def get_joker_click_position(self, pos, joker_options):
        joker_y = 300  # Position joker options in center
        total_joker_width = len(joker_options) * 100 + (len(joker_options) - 1) * 10  # CARD_WIDTH = 100
        joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
        for i, joker in enumerate(joker_options):
            x = joker_start_x + i * (100 + 10)  # CARD_WIDTH + 10
            joker_rect = pygame.Rect(x, joker_y, 100, 140)  # CARD_WIDTH, CARD_HEIGHT
            if joker_rect.collidepoint(pos):
                return i
        return None

    def get_owned_joker_click_position(self, pos, jokers):
        if jokers:
            joker_y = 50
            total_joker_width = len(jokers) * 100 + (len(jokers) - 1) * 10  # CARD_WIDTH = 100
            joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
            for i, joker in enumerate(jokers):
                x = joker_start_x + i * (100 + 10)  # CARD_WIDTH + 10
                joker_rect = pygame.Rect(x, joker_y, 100, 140)  # CARD_WIDTH, CARD_HEIGHT
                if joker_rect.collidepoint(pos):
                    return i
        return None