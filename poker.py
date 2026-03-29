# Poker hand evaluation - using hash tables (dictionaries) for counting
def evaluate_poker_hand(cards):
    values = [card.value for card in cards]
    suits = [card.suit for card in cards]
    
    values.sort()

    # Count occurrences of each value and suit
    value_counts = {}
    suit_counts = {}
    for value in values:
        value_counts[value] = value_counts.get(value, 0) + 1
    for suit in suits:
        suit_counts[suit] = suit_counts.get(suit, 0) + 1
    
    # Check for flush and straight
    is_flush = len(suit_counts) == 1
    is_straight = values == list(range(values[0], values[0] + len(cards)))
    
    # Determine hand type
    if len(cards) == 1:
        hand = "High Card"
    elif len(cards) == 2:
        if 2 in value_counts.values():
            hand = "Pair"
        else:
            hand = "High Card"
    elif len(cards) == 3:
        if 3 in value_counts.values():
            hand = "Three of a Kind"
        else:
            hand = "High Card"
    elif len(cards) == 4:
        if 4 in value_counts.values():
            hand = "Four of a Kind"
        else:
            hand = "High Card"
    elif len(cards) == 5:
        if is_flush and is_straight:
            hand = "Straight Flush"
        elif 4 in value_counts.values():
            hand = "Four of a Kind"
        elif 3 in value_counts.values() and 2 in value_counts.values():
            hand = "Full House"
        elif is_flush:
            hand = "Flush"
        elif is_straight:
            hand = "Straight"
        elif 3 in value_counts.values():
            hand = "Three of a Kind"
        elif list(value_counts.values()).count(2) == 2:
            hand = "Two Pair"
        elif 2 in value_counts.values():
            hand = "Pair"
        else:
            hand = "High Card"
    
    # Base chips and multiplier for each hand
    base_mult = {
        "Straight Flush": (100, 8),
        "Four of a Kind": (60, 7),
        "Full House": (40, 4),
        "Flush": (35, 4),
        "Straight": (30, 4),
        "Three of a Kind": (30, 3),
        "Two Pair": (20, 2),
        "Pair": (10, 2),
        "High Card": (5, 1)
    }
    
    base, mult = base_mult[hand]
    total_value = sum(values)
    chips = (base + total_value) * mult
    score = chips  # Final score is the chips
    
    return hand, score, chips
