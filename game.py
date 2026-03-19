import pygame
import random
from card import Card, Deck
from ui import Button, UIManager
from poker import evaluate_poker_hand

# Joker class - special cards with abilities
class Joker:
    def __init__(self, name, description, effect_type, effect_value):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # 'multiplier_bonus', 'chip_bonus', etc.
        self.effect_value = effect_value
        self.image = None  # Initialize to None, load lazily

    def load_image(self):
        if self.image is not None:
            return  # Already loaded

        # For now, create a colored rectangle with text
        self.image = pygame.Surface((100, 140))  # CARD_WIDTH, CARD_HEIGHT
        self.image.fill((0, 0, 255))  # Blue background for jokers

        # Draw joker name
        font = pygame.font.Font(None, 24)
        name_surface = font.render(self.name[:10], True, (255, 255, 255))  # Truncate if too long
        name_rect = name_surface.get_rect(center=(50, 70))  # CARD_WIDTH//2, CARD_HEIGHT//2
        self.image.blit(name_surface, name_rect)

    def draw(self, screen, x, y):
        if self.image is None:
            self.load_image()
        screen.blit(self.image, (x, y))

    def apply_effect(self, base_score, multiplier):
        if self.effect_type == 'multiplier_bonus':
            return base_score, multiplier + self.effect_value
        elif self.effect_type == 'chip_bonus':
            return base_score + self.effect_value, multiplier
        return base_score, multiplier

# Available jokers pool
JOKER_POOL = [
    Joker("The Chud", "+5 Multiplier", "multiplier_bonus", 5),
    # Add more jokers here as we create them
]

# Game class - main game logic using composition
class Game:
    def __init__(self):
        self.deck = Deck()  # Composition: Game has a Deck
        self.deck.shuffle()
        self.hand = []  # List to store drawn cards
        self.selected = set()  # Set to track selected card indices
        self.jokers = []  # List to store collected jokers (max 5)
        self.joker_options = []  # Temporary list for joker selection
        self.selecting_joker = False  # Flag for joker selection mode
        self.current_score = 0
        self.target_score = 300  # For first round
        self.discards_left = 4
        self.turns_left = 4  # 4 turns per round
        self.current_round = 1
        self.ui_manager = UIManager()  # Composition: Game has a UIManager
        self.play_button = Button(1200 // 2 - 150 - 10, 800 - 100, 150, 50, "Play Hand")  # SCREEN_WIDTH // 2 - BUTTON_WIDTH - 10
        self.discard_button = Button(1200 // 2 + 10, 800 - 100, 150, 50, "Discard & Draw", (255, 0, 0))  # RED
        self.draw_initial_hand()

    def draw_initial_hand(self):
        self.hand = []
        for _ in range(8):  # Draw 8 cards initially
            card = self.deck.draw_card()
            if card:
                self.hand.append(card)

    def draw_hand(self, num_cards):
        drawn = []
        for _ in range(num_cards):
            card = self.deck.draw_card()
            if card:
                drawn.append(card)
        return drawn

    def play_hand(self):
        if len(self.selected) >= 1 and len(self.selected) <= 5 and self.turns_left > 0:
            selected_cards = [self.hand[i] for i in self.selected]
            hand_type, base_score, base_chips = evaluate_poker_hand(selected_cards)
            if hand_type:
                # Apply joker effects
                multiplier = 1
                for joker in self.jokers:
                    base_score, multiplier = joker.apply_effect(base_score, multiplier)

                score = base_score * multiplier
                self.current_score += score
                print(f"Played {hand_type}: +{score} chips (Total: {self.current_score})")

            # Remove played cards and draw new ones to maintain hand size
            self.hand = [card for i, card in enumerate(self.hand) if i not in self.selected]
            new_cards = self.draw_hand(len(self.selected))
            self.hand.extend(new_cards)
            self.selected.clear()
            self.turns_left -= 1
            self.check_round_end()
            return True
        return False

    def discard_and_draw(self):
        if len(self.selected) <= 5 and self.discards_left > 0 and self.turns_left > 0:
            # Remove selected cards
            self.hand = [card for i, card in enumerate(self.hand) if i not in self.selected]
            # Draw new cards to maintain 8 cards
            num_to_draw = 8 - len(self.hand)
            new_cards = self.draw_hand(num_to_draw)
            self.hand.extend(new_cards)
            self.selected.clear()
            self.discards_left -= 1
            print(f"Discarded {len(self.selected)} cards. {self.discards_left} discards left.")

    def check_round_end(self):
        if self.turns_left == 0:
            if self.current_score >= self.target_score:
                print(f"Round {self.current_round} completed! Score: {self.current_score}/{self.target_score}")
                self.show_joker_selection()
            else:
                print(f"Round {self.current_round} failed! Score: {self.current_score}/{self.target_score}")
                # Could add game over logic here

    def show_joker_selection(self):
        # Randomly select 4 jokers from the pool
        available_jokers = [joker for joker in JOKER_POOL if joker not in self.jokers]
        if len(available_jokers) >= 4:
            self.joker_options = random.sample(available_jokers, 4)
        else:
            self.joker_options = available_jokers  # Take all available if less than 4
        self.selecting_joker = True

    def select_joker(self, joker):
        if len(self.jokers) < 5:  # Max 5 jokers
            self.jokers.append(joker)
        self.joker_options = []
        self.selecting_joker = False
        self.next_round()

    def next_round(self):
        self.current_round += 1
        self.target_score += 200  # Increase target for next round
        self.turns_left = 4
        self.discards_left = 4
        self.current_score = 0  # Reset score for new round
        self.deck = Deck()  # New deck for new round
        self.deck.shuffle()
        self.draw_initial_hand()
        print(f"Starting Round {self.current_round} - Target: {self.target_score}")

    def handle_click(self, pos):
        # Handle joker selection first if active
        if self.selecting_joker and self.joker_options:
            joker_index = self.ui_manager.get_joker_click_position(pos, self.joker_options)
            if joker_index is not None:
                self.select_joker(self.joker_options[joker_index])
                return

        # Handle card selection
        card_index = self.ui_manager.get_hand_click_position(pos, self.hand)
        if card_index is not None:
            if card_index in self.selected:
                self.selected.remove(card_index)
            elif len(self.selected) < 5:
                self.selected.add(card_index)
            return

        # Handle button clicks
        if self.play_button.is_clicked(pos):
            self.play_hand()
        elif self.discard_button.is_clicked(pos):
            self.discard_and_draw()

    def draw(self, screen):
        # Draw background
        screen.fill((255, 255, 255))  # WHITE

        # Draw jokers at top center
        self.ui_manager.draw_jokers(screen, self.jokers)

        # Draw joker selection screen
        if self.selecting_joker and self.joker_options:
            self.ui_manager.draw_joker_selection(screen, self.joker_options)
        else:
            # Draw normal game UI
            self.ui_manager.draw_hand(screen, self.hand, self.selected)
            self.play_button.draw(screen)
            self.discard_button.draw(screen)

        # Draw score info (always visible)
        self.ui_manager.draw_score_info(screen, self.current_score, self.target_score,
                                      self.current_round, self.turns_left, self.discards_left)

        pygame.display.flip()