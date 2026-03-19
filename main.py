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
                    game.handle_click(event.pos)

        game.draw(screen)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

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

# Joker class - special cards with abilities
class Joker:
    def __init__(self, name, description, effect_type, effect_value):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # 'multiplier_bonus', 'chip_bonus', etc.
        self.effect_value = effect_value
        self.image = None
        self.load_image()

    def load_image(self):
        # For now, create a colored rectangle with text
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill(BLUE)  # Blue background for jokers
        
        # Draw joker name
        name_surface = small_font.render(self.name[:10], True, WHITE)  # Truncate if too long
        name_rect = name_surface.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
        self.image.blit(name_surface, name_rect)

    def draw(self, screen, x, y):
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
        random.shuffle(self.cards)  # Shuffle the list in place

    def draw_card(self):
        if self.cards:
            return self.cards.pop()  # Remove and return the last card
        return None

# Button class - for user interaction
class Button:
    def __init__(self, x, y, width, height, text, color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Poker hand evaluation - using hash tables (dictionaries) for counting
def evaluate_poker_hand(cards):
    if len(cards) < 1 or len(cards) > 5:
        return None, 0, 0

    # Sort cards by value for straight detection
    sorted_cards = sorted(cards, key=lambda c: c.value)
    values = [c.value for c in sorted_cards]
    suits = [c.suit for c in sorted_cards]

    # Check for flush (all same suit) - only if 5 cards
    is_flush = len(set(suits)) == 1 if len(cards) == 5 else False

    # Check for straight - only if 5 cards
    is_straight = False
    if len(cards) == 5:
        is_straight = all(values[i] + 1 == values[i+1] for i in range(4))
        # Special case: Ace-low straight (A,2,3,4,5)
        if not is_straight and set(values) == {1, 2, 3, 4, 5}:
            is_straight = True

    # Count frequencies using Counter (hash table)
    value_counts = Counter(values)
    counts = sorted(value_counts.values(), reverse=True)

    # Determine hand type
    hand_type = ""
    base_chips = sum(c.chip_value for c in cards)
    multiplier = 1

    if len(cards) == 5:
        if is_straight and is_flush:
            hand_type = "Straight Flush"
            multiplier = 8
        elif 4 in counts:
            hand_type = "Four of a Kind"
            multiplier = 7
        elif counts == [3, 2]:
            hand_type = "Full House"
            multiplier = 4
        elif is_flush:
            hand_type = "Flush"
            multiplier = 4
        elif is_straight:
            hand_type = "Straight"
            multiplier = 4
        elif 3 in counts:
            hand_type = "Three of a Kind"
            multiplier = 3
        elif counts == [2, 2, 1]:
            hand_type = "Two Pair"
            multiplier = 2
        elif 2 in counts:
            hand_type = "Pair"
            multiplier = 2
        else:
            hand_type = "High Card"
            multiplier = 1
    else:
        # For partial hands (1-4 cards)
        if len(cards) == 4 and counts == [2, 2]:
            hand_type = "Two Pair"
            multiplier = 2
        elif len(cards) == 3 and 3 in counts:
            hand_type = "Three of a Kind"
            multiplier = 3
        elif len(cards) == 2 and 2 in counts:
            hand_type = "Pair"
            multiplier = 2
        else:
            hand_type = f"{len(cards)} Cards"
            multiplier = 1

    # Calculate base chips for the hand type
    hand_base = {
        "Straight Flush": 100,
        "Four of a Kind": 60,
        "Full House": 40,
        "Flush": 35,
        "Straight": 30,
        "Three of a Kind": 30,
        "Two Pair": 20,
        "Pair": 10,
        "High Card": 5,
        "1 Cards": 1,
        "2 Cards": 2,
        "3 Cards": 3,
        "4 Cards": 4
    }.get(hand_type, 1)

    total_score = hand_base * multiplier

    return hand_type, total_score, base_chips

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
        self.play_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH - 10, SCREEN_HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT, "Play Hand")
        self.discard_button = Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT, "Discard & Draw", RED)
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
                self.next_round()
            else:
                print(f"Round {self.current_round} failed! Score: {self.current_score}/{self.target_score}")
                # Could add game over logic here

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
        # Sort hand by rank for click detection (Ace low for sorting)
        sorted_hand = sorted(self.hand, key=lambda c: c.value)

        # Calculate centered position for hand
        total_hand_width = len(sorted_hand) * CARD_WIDTH + (len(sorted_hand) - 1) * 10
        start_x = (SCREEN_WIDTH - total_hand_width) // 2
        y = SCREEN_HEIGHT - 250  # Position higher above buttons

        # Check card clicks
        for i, card in enumerate(sorted_hand):
            x = start_x + i * (CARD_WIDTH + 10)
            card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            if card_rect.collidepoint(pos):
                # Find original index in unsorted hand
                orig_index = self.hand.index(card)
                if orig_index in self.selected:
                    self.selected.remove(orig_index)
                elif len(self.selected) < 5:
                    self.selected.add(orig_index)
                return

        # Check joker clicks for selection
        if self.selecting_joker and self.joker_options:
            joker_y = 300  # Position joker options in center
            total_joker_width = len(self.joker_options) * CARD_WIDTH + (len(self.joker_options) - 1) * 10
            joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
            for i, joker in enumerate(self.joker_options):
                x = joker_start_x + i * (CARD_WIDTH + 10)
                joker_rect = pygame.Rect(x, joker_y, CARD_WIDTH, CARD_HEIGHT)
                if joker_rect.collidepoint(pos):
                    self.select_joker(joker)
                    return

        # Check button clicks
        if self.play_button.is_clicked(pos):
            self.play_hand()
        elif self.discard_button.is_clicked(pos):
            self.discard_and_draw()

    def draw(self, screen):
        # Draw background
        screen.fill(WHITE)

        # Sort hand by rank for display (Ace low for sorting)
        sorted_hand = sorted(self.hand, key=lambda c: c.value)

        # Calculate centered position for hand
        total_hand_width = len(sorted_hand) * CARD_WIDTH + (len(sorted_hand) - 1) * 10
        start_x = (SCREEN_WIDTH - total_hand_width) // 2
        y = SCREEN_HEIGHT - 250  # Position higher above buttons

        # Draw hand
        for i, card in enumerate(sorted_hand):
            x = start_x + i * (CARD_WIDTH + 10)
            # Check if this card is selected (find original index)
            orig_index = self.hand.index(card)
            selected = orig_index in self.selected
            card.draw(screen, x, y, selected)

        # Draw jokers at top center
        if self.jokers:
            joker_y = 50
            total_joker_width = len(self.jokers) * CARD_WIDTH + (len(self.jokers) - 1) * 10
            joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
            for i, joker in enumerate(self.jokers):
                x = joker_start_x + i * (CARD_WIDTH + 10)
                joker.draw(screen, x, joker_y)

        # Draw joker selection screen
        if self.selecting_joker and self.joker_options:
            # Dim background
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            # Draw joker options
            joker_y = 300
            total_joker_width = len(self.joker_options) * CARD_WIDTH + (len(self.joker_options) - 1) * 10
            joker_start_x = (SCREEN_WIDTH - total_joker_width) // 2
            for i, joker in enumerate(self.joker_options):
                x = joker_start_x + i * (CARD_WIDTH + 10)
                joker.draw(screen, x, joker_y)
                
                # Draw description below each joker
                desc_surface = small_font.render(joker.description, True, WHITE)
                desc_rect = desc_surface.get_rect(center=(x + CARD_WIDTH//2, joker_y + CARD_HEIGHT + 20))
                screen.blit(desc_surface, desc_rect)
            
            # Draw selection prompt
            prompt_text = "Choose a Joker!"
            prompt_surface = font.render(prompt_text, True, WHITE)
            prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
            screen.blit(prompt_surface, prompt_rect)

        # Draw buttons
        self.play_button.draw(screen)
        self.discard_button.draw(screen)

        # Draw scores and info
        score_text = f"Score: {self.current_score} / {self.target_score}"
        score_surface = font.render(score_text, True, BLACK)
        screen.blit(score_surface, (10, 10))

        round_text = f"Round: {self.current_round}"
        round_surface = small_font.render(round_text, True, BLACK)
        screen.blit(round_surface, (10, 40))

        turns_text = f"Turns Left: {self.turns_left}"
        turns_surface = small_font.render(turns_text, True, BLACK)
        screen.blit(turns_surface, (10, 60))

        discards_text = f"Discards Left: {self.discards_left}"
        discards_surface = small_font.render(discards_text, True, BLACK)
        screen.blit(discards_surface, (10, 80))

        pygame.display.flip()

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
                    game.handle_click(event.pos)

        game.draw(screen)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
