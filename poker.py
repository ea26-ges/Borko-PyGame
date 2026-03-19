from collections import Counter

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