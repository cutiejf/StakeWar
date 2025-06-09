import pygame
import time
import random

# Screen + Card sizes
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 100, 100
CARD_SPACING = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WAR TIME")
font_small = pygame.font.SysFont('Arial', 20)
font_medium = pygame.font.SysFont('Arial', 30)
font_large = pygame.font.SysFont('Arial', 60)
font_tally = pygame.font.SysFont('Arial', 16)

# Load images
card_images = {}
suits = {'H': 'hearts', 'D': 'diamonds', 'C': 'clubs', 'S': 'spades'}
values = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
for value in values:
    for suit, suit_name in suits.items():
        v = value.zfill(2) if value.isdigit() and int(value) < 10 else value
        filename = f"cards/card_{suit_name}_{v}.png"
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        card_images[value + suit] = image

card_back = pygame.image.load("cards/card_back.png").convert_alpha()
card_back = pygame.transform.scale(card_back, (CARD_WIDTH, CARD_HEIGHT))

# Load table image
table_image = pygame.image.load("table.png").convert()
table_image = pygame.transform.scale(table_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Game state variables
chip_pile = 10000
main_bet = 50
side_bet_tie = 0
side_bet_suited = 0
wars_lost = 0
auto_bet = False
auto_hands = 0
AUTO_HANDS_MAX = 50
last_bets = {"main": 50, "tie": 0, "suited": 0}
starting_chips = chip_pile  # For profit/loss

# Initialize payout tally
payout_tally = {
    "main_2x": 0, "main_0x": 0, "main_tie": 0,
    "main_2.5x": 0, "main_3.5x": 0, "main_5x": 0, "main_100x": 0,
    "side_tie": 0, "side_suited": 0, "side_suited+win": 0,
    "wars_lost": 0
}

# Button definitions
buttons = [
    {"label": "Main +10", "rect": pygame.Rect(10, SCREEN_HEIGHT-190, 70, 30), "action": "main_up", "color": (100, 100, 255)},
    {"label": "Main -10", "rect": pygame.Rect(90, SCREEN_HEIGHT-190, 70, 30), "action": "main_down", "color": (100, 100, 255)},
    {"label": "Tie +5", "rect": pygame.Rect(10, SCREEN_HEIGHT-150, 70, 30), "action": "tie_up", "color": (50, 200, 50)},
    {"label": "Tie -5", "rect": pygame.Rect(90, SCREEN_HEIGHT-150, 70, 30), "action": "tie_down", "color": (50, 200, 50)},
    {"label": "Suited +5", "rect": pygame.Rect(10, SCREEN_HEIGHT-110, 70, 30), "action": "suited_up", "color": (200, 50, 200)},
    {"label": "Suited -5", "rect": pygame.Rect(90, SCREEN_HEIGHT-110, 70, 30), "action": "suited_down", "color": (200, 50, 200)},
    {"label": "Confirm", "rect": pygame.Rect(10, SCREEN_HEIGHT-70, 150, 30), "action": "confirm", "color": (255, 200, 0)},
]
auto_button = {"label": "Auto", "rect": pygame.Rect(10, SCREEN_HEIGHT-30, 150, 30), "action": "toggle_auto", "color": (255, 100, 0)}

def card_value(card):
    val = card[:-1]
    face_values = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    if val in face_values:
        return face_values[val]
    return int(val)

def get_card_name(card):
    name_map = {'2': 'Two', '3': 'Three', '4': 'Four', '5': 'Five',
                '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Nine', '10': 'Ten',
                'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
    return name_map[card[:-1]]

def draw_centered_text(text, font, surface, x, y, color=(255, 255, 255)):
    rendered = font.render(text, True, color)
    text_x = x - rendered.get_width() // 2
    text_y = y - rendered.get_height() // 2
    surface.blit(rendered, (text_x, text_y))

def draw_tally():
    y = 10
    rendered = font_tally.render(f"Wars Lost: {wars_lost}", True, (255, 100, 100))
    screen.blit(rendered, (10, y))
    y += 20
    for payout, count in payout_tally.items():
        text = f"{payout}: {count}"
        rendered = font_tally.render(text, True, (255, 255, 255))
        screen.blit(rendered, (10, y))
        y += 20

def draw_profit_loss():
    profit = chip_pile - starting_chips
    color = (50, 255, 50) if profit >= 0 else (255, 80, 80)
    text = f"Profit/Loss: {'+' if profit >= 0 else ''}{profit}"
    rendered = font_medium.render(text, True, color)
    padding = 10
    screen.blit(rendered, (SCREEN_WIDTH - rendered.get_width() - padding, padding))

def draw_bets_bottom():
    padding = 20
    y = SCREEN_HEIGHT - (32 * 6) - padding  # Make room for Total Bet
    total_bet = main_bet + side_bet_tie + side_bet_suited
    items = [
        ("Chips:", chip_pile, (255, 255, 0)),
        ("Main Bet:", main_bet, (200, 200, 255)),
        ("Tie Bet:", side_bet_tie, (50, 255, 50)),
        ("Suited Bet:", side_bet_suited, (255, 50, 255)),
        ("Total Bet:", total_bet, (255, 255, 255)),
        (
            f"Auto: {'On (' + str(AUTO_HANDS_MAX - auto_hands) + ' left)' if auto_bet else 'Off'}",
            "",
            (255, 150, 0) if auto_bet else (180, 180, 180)
        ),
    ]
    for label, value, color in items:
        text = f"{label} {value}".strip()
        rendered = font_medium.render(text, True, color)
        screen.blit(rendered, (SCREEN_WIDTH - rendered.get_width() - padding, y))
        y += 32

def draw_auto_button():
    mouse_pos = pygame.mouse.get_pos()
    if auto_bet:
        fill_color = (255, 80, 80)  # Red for STOP AUTO
        label = "STOP AUTO"
    else:
        fill_color = auto_button["color"]
        label = "Auto"
    if auto_button["rect"].collidepoint(mouse_pos):
        fill_color = tuple(min(c + 50, 255) for c in fill_color)
    pygame.draw.rect(screen, fill_color, auto_button["rect"])
    draw_centered_text(label, font_tally, screen, auto_button["rect"].centerx, auto_button["rect"].centery, (255, 255, 255))

def draw_border(winner, cards=None, card_index=None, tie=False):
    if tie:
        if cards and card_index is not None:
            total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
            start_x = (SCREEN_WIDTH - total_width) // 2
            for idx in card_index:
                pos_x = start_x + idx * (CARD_WIDTH + CARD_SPACING)
                pos_y = 50 if winner == "house" else SCREEN_HEIGHT - CARD_HEIGHT - 50
                pygame.draw.rect(screen, (255, 255, 0), (pos_x - 5, pos_y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
        else:
            pygame.draw.rect(screen, (255, 255, 0), ((SCREEN_WIDTH - CARD_WIDTH) // 2 - 5, SCREEN_HEIGHT - CARD_HEIGHT - 50 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
            pygame.draw.rect(screen, (255, 255, 0), ((SCREEN_WIDTH - CARD_WIDTH) // 2 - 5, 50 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
    else:
        if winner == "player":
            if cards and card_index is not None:
                total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
                start_x = (SCREEN_WIDTH - total_width) // 2
                pos_x = start_x + card_index * (CARD_WIDTH + CARD_SPACING)
                pos_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
                pygame.draw.rect(screen, (0, 255, 0), (pos_x - 5, pos_y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
            else:
                pygame.draw.rect(screen, (0, 255, 0), ((SCREEN_WIDTH - CARD_WIDTH) // 2 - 5, SCREEN_HEIGHT - CARD_HEIGHT - 50 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
        elif winner == "house":
            if cards and card_index is not None:
                total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
                start_x = (SCREEN_WIDTH - total_width) // 2
                pos_x = start_x + card_index * (CARD_WIDTH + CARD_SPACING)
                pos_y = 50
                pygame.draw.rect(screen, (255, 0, 0), (pos_x - 5, pos_y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
            else:
                pygame.draw.rect(screen, (255, 0, 0), ((SCREEN_WIDTH - CARD_WIDTH) // 2 - 5, 50 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()
    time.sleep(0.5)

def show_popup(message, payout, result, player_cards=None, house_cards=None, reveal_level=0, winner=None, card_index=None, tie=False, multiplier=None):
    screen.blit(table_image, (0, 0))
    # Redraw cards
    if player_cards and len(player_cards) > 1:
        total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, card in enumerate(player_cards):
            pos_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
            pos_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
            if reveal_level > 0 and i >= (3 - reveal_level):
                screen.blit(card_images[card], (pos_x, pos_y))
            else:
                screen.blit(card_back, (pos_x, pos_y))
        for i, card in enumerate(house_cards):
            pos_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
            pos_y = 50
            if reveal_level > 0 and i >= (3 - reveal_level):
                screen.blit(card_images[card], (pos_x, pos_y))
            else:
                screen.blit(card_back, (pos_x, pos_y))
    elif player_cards:
        screen.blit(card_images[player_cards[0]], ((SCREEN_WIDTH - CARD_WIDTH) // 2, SCREEN_HEIGHT - CARD_HEIGHT - 50))
        screen.blit(card_images[house_cards[0]], ((SCREEN_WIDTH - CARD_WIDTH) // 2, 50))
    # Redraw border if applicable
    if tie:
        if player_cards and len(player_cards) > 1 and card_index is not None:
            draw_border("player", player_cards, card_index=[card_index, card_index], tie=True)
            draw_border("house", house_cards, card_index=[card_index, card_index], tie=True)
        else:
            draw_border(None, None, tie=True)
    elif winner == "player":
        if card_index is not None:
            draw_border("player", player_cards, card_index, tie=False)
        else:
            draw_border("player", None, None, tie=False)
    elif winner == "house":
        if card_index is not None:
            draw_border("house", house_cards, card_index, tie=False)
        else:
            draw_border("house", None, None, tie=False)
    # Draw popup
    popup = pygame.Surface((340, 170))
    popup.fill((0, 0, 0))
    pygame.draw.rect(popup, (255, 215, 0), popup.get_rect(), 5)
    color = (50, 200, 50) if "Player" in message or "Triple" in message else (200, 50, 50) if "House" in message else (255, 255, 255)

    payout_str = str(payout)
    # Use multiplier if provided, else try to infer
    if multiplier is not None:
        if isinstance(multiplier, float) and not multiplier.is_integer():
            big_text = f"{multiplier:.2f}x = {payout_str}"
        else:
            big_text = f"{int(multiplier)}x = {payout_str}"
    elif "x" in payout_str:
        big_text = payout_str
    else:
        # Try to infer multiplier from message
        if "100x" in message:
            big_text = f"100x = {payout_str}"
        elif "5x" in message:
            big_text = f"5x = {payout_str}"
        elif "3.5x" in message:
            big_text = f"3.5x = {payout_str}"
        elif "2.5x" in message:
            big_text = f"2.5x = {payout_str}"
        elif "2x" in message:
            big_text = f"2x = {payout_str}"
        elif "3x" in message:
            big_text = f"3x = {payout_str}"
        else:
            big_text = payout_str
    small_text = f"Total Pay: {payout_str}"

    draw_centered_text(message, font_small, popup, 170, 30, color)
    draw_centered_text(big_text, font_large, popup, 170, 80, (255, 255, 255))
    draw_centered_text(small_text, font_small, popup, 170, 130, (200, 200, 200))
    draw_centered_text(result, font_small, popup, 170, 155, (255, 255, 255))
    popup_x = (SCREEN_WIDTH - popup.get_width()) // 2
    popup_y = (SCREEN_HEIGHT - popup.get_height()) // 2
    screen.blit(popup, (popup_x, popup_y))
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()
    time.sleep(1.5)
    screen.blit(table_image, (0, 0))

def show_war_popup():
    popup = pygame.Surface((340, 170))
    popup.fill((0, 0, 0))
    pygame.draw.rect(popup, (255, 0, 0), popup.get_rect(), 8)
    draw_centered_text("WAR!", font_large, popup, 170, 85, (255, 255, 0))
    popup_x = (SCREEN_WIDTH - popup.get_width()) // 2
    popup_y = (SCREEN_HEIGHT - popup.get_height()) // 2
    screen.blit(popup, (popup_x, popup_y))
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()
    time.sleep(1.2)
    screen.blit(table_image, (0, 0))

def draw_table():
    screen.blit(table_image, (0, 0))
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()

def draw_single_card(card, position, face_up=True):
    x = (SCREEN_WIDTH - CARD_WIDTH) // 2
    y = SCREEN_HEIGHT - CARD_HEIGHT - 50 if position == 0 else 50
    if face_up:
        screen.blit(card_images[card], (x, y))
    else:
        screen.blit(card_back, (x, y))
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()

def draw_war_cards(player_cards, house_cards, reveal_level=0):
    screen.blit(table_image, (0, 0))
    total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_width) // 2
    for i, card in enumerate(player_cards):
        pos_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
        pos_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
        if reveal_level > 0 and i >= (3 - reveal_level):
            screen.blit(card_images[card], (pos_x, pos_y))
        else:
            screen.blit(card_back, (pos_x, pos_y))
    for i, card in enumerate(house_cards):
        pos_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
        pos_y = 50
        if reveal_level > 0 and i >= (3 - reveal_level):
            screen.blit(card_images[card], (pos_x, pos_y))
        else:
            screen.blit(card_back, (pos_x, pos_y))
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()

def draw_bet_buttons():
    mouse_pos = pygame.mouse.get_pos()
    valid_bets = main_bet >= 50 and (main_bet + side_bet_tie + side_bet_suited) <= chip_pile
    for button in buttons:
        fill_color = button["color"]
        if button["rect"].collidepoint(mouse_pos):
            fill_color = tuple(min(c + 50, 255) for c in fill_color)
        if button["action"] == "confirm" and not valid_bets:
            fill_color = (100, 100, 100)
        pygame.draw.rect(screen, fill_color, button["rect"])
        draw_centered_text(button["label"], font_tally, screen, button["rect"].centerx, button["rect"].centery, (255, 255, 255))
    draw_auto_button()
    draw_profit_loss()

def get_bets():
    global main_bet, side_bet_tie, side_bet_suited, auto_bet, auto_hands
    getting_bets = True
    error_message = ""
    while getting_bets:
        screen.blit(table_image, (0, 0))
        draw_tally()
        draw_bets_bottom()
        draw_bet_buttons()
        if error_message:
            draw_centered_text(error_message, font_small, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-250, (255, 0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                error_message = ""
                for button in buttons + [auto_button]:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["action"] == "main_up" and main_bet + 10 <= chip_pile - side_bet_tie - side_bet_suited:
                            main_bet += 10
                        elif button["action"] == "main_down" and main_bet - 10 >= 50:
                            main_bet -= 10
                        elif button["action"] == "tie_up" and side_bet_tie + 5 <= chip_pile - main_bet - side_bet_suited:
                            side_bet_tie += 5
                        elif button["action"] == "tie_down" and side_bet_tie - 5 >= 0:
                            side_bet_tie -= 5
                        elif button["action"] == "suited_up" and side_bet_suited + 5 <= chip_pile - main_bet - side_bet_tie:
                            side_bet_suited += 5
                        elif button["action"] == "suited_down" and side_bet_suited - 5 >= 0:
                            side_bet_suited -= 5
                        elif button["action"] == "confirm":
                            if main_bet >= 50 and (main_bet + side_bet_tie + side_bet_suited) <= chip_pile:
                                getting_bets = False
                            else:
                                error_message = "Invalid bets: Main ≥ 50, Total ≤ Chips"
                        elif button["action"] == "toggle_auto":
                            if not auto_bet:
                                auto_bet = True
                                auto_hands = 0
                            else:
                                auto_bet = False
                                auto_hands = 0
                            draw_table()  # Instantly update button
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    auto_bet = False
                    auto_hands = 0

def create_shuffled_deck():
    deck = [v + s for v in values for s in suits.keys()]
    random.shuffle(deck)
    return deck

def play_regular_round():
    global chip_pile, wars_lost, main_bet, side_bet_tie, side_bet_suited, last_bets, auto_bet, auto_hands
    if auto_bet:
        main_bet = last_bets["main"]
        side_bet_tie = last_bets["tie"]
        side_bet_suited = last_bets["suited"]
        if main_bet < 50 or (main_bet + side_bet_tie + side_bet_suited) > chip_pile:
            auto_bet = False
            auto_hands = 0
            draw_table()
    else:
        get_bets()
    total_bet = main_bet + side_bet_tie + side_bet_suited
    chip_pile -= total_bet
    last_bets = {"main": main_bet, "tie": side_bet_tie, "suited": side_bet_suited}
    deck = create_shuffled_deck()
    draw_table()
    time.sleep(0.5)
    player_card = deck.pop(0)
    house_card = deck.pop(0)
    draw_single_card(player_card, 0)
    time.sleep(0.8)
    draw_single_card(house_card, 1)
    time.sleep(1.2)
    p_val = card_value(player_card)
    h_val = card_value(house_card)
    # Side bet: Tie
    tie_win = False
    tie_payout = 0
    if p_val == h_val and side_bet_tie > 0:
        tie_payout = side_bet_tie * 3
        chip_pile += tie_payout
        payout_tally["side_tie"] += 1
        tie_win = True
    # Side bet: Suited
    suited_win = False
    suited_payout = 0
    if player_card[-1] == house_card[-1] and side_bet_suited > 0:
        suited_payout = side_bet_suited * 3
        chip_pile += suited_payout
        payout_tally["side_suited"] += 1
        suited_win = True
    # Main bet
    main_payout = 0
    suited_bonus = 0
    if p_val > h_val:
        main_payout = main_bet * 2
        chip_pile += main_payout
        payout_tally["main_2x"] += 1
        if suited_win:
            suited_bonus = side_bet_suited * 2
            chip_pile += suited_bonus
            payout_tally["side_suited+win"] += 1
        draw_border("player")
        total_payout = main_payout + tie_payout + suited_payout + suited_bonus
        multiplier = total_payout / total_bet if total_bet else None
        show_popup("Player Wins!", f"{total_payout}", f"{get_card_name(player_card)} beats {get_card_name(house_card)}",
                   player_cards=[player_card], house_cards=[house_card], winner="player", multiplier=multiplier)
        return total_payout
    elif h_val > p_val:
        payout_tally["main_0x"] += 1
        draw_border("house")
        total_payout = tie_payout + suited_payout
        msg = "House Wins!"
        if total_payout > 0:
            msg += f" (Side Bet Win: {total_payout})"
        multiplier = total_payout / total_bet if total_bet else None
        show_popup(msg, f"{total_payout}", f"{get_card_name(house_card)} beats {get_card_name(player_card)}",
                   player_cards=[player_card], house_cards=[house_card], winner="house", multiplier=multiplier)
        return total_payout
    else:
        payout_tally["main_tie"] += 1
        draw_border(None, None, tie=True)
        total_payout = tie_payout + suited_payout
        multiplier = total_payout / total_bet if total_bet else None
        show_popup("Player House Tie", f"{total_payout}", f"{get_card_name(player_card)} equals {get_card_name(house_card)}",
                   player_cards=[player_card], house_cards=[house_card], tie=True, multiplier=multiplier)
        show_war_popup()
        time.sleep(0.5)
        return play_war_round(deck, total_bet)

def play_war_round(deck, total_bet):
    global wars_lost, chip_pile, main_bet
    if len(deck) < 6:
        show_popup("Deck Empty", 1.0, "Starting fresh hand...", player_cards=[], house_cards=[], multiplier=1.0)
        return 1.0
    player_cards = [deck.pop(0) for _ in range(3)]
    house_cards = [deck.pop(0) for _ in range(3)]

    # 1. Show all cards face down for suspense
    draw_war_cards(['XX']*3, ['XX']*3, 0)  # Use 'XX' as a placeholder for face down
    pygame.display.flip()
    time.sleep(0.7)

    # 2. Reveal each war card, one at a time
    for i in reversed(range(3)):
        # Reveal player's card
        temp_player = ['XX']*3
        temp_house = ['XX']*3
        temp_player[i] = player_cards[i]
        draw_war_cards(temp_player, temp_house, 0)
        pygame.display.flip()
        time.sleep(0.5)

        # Reveal house's card
        temp_house[i] = house_cards[i]
        draw_war_cards(temp_player, temp_house, 0)
        pygame.display.flip()
        time.sleep(0.5)

        # Evaluate this war
        p_val = card_value(player_cards[i])
        h_val = card_value(house_cards[i])
        if p_val > h_val:
            if i == 2:
                payout = main_bet * 2.5
                payout_tally["main_2.5x"] += 1
            elif i == 1:
                payout = main_bet * 3.5
                payout_tally["main_3.5x"] += 1
            else:
                payout = main_bet * 5
                payout_tally["main_5x"] += 1
            chip_pile += int(payout)
            multiplier = payout / total_bet if total_bet else None
            show_popup("Player Wins War!", f"{payout}", f"{get_card_name(player_cards[i])} beats {get_card_name(house_cards[i])}",
                       player_cards=player_cards, house_cards=house_cards, reveal_level=3-i, winner="player", card_index=i, multiplier=multiplier)
            return payout
        elif h_val > p_val:
            wars_lost += 1
            payout_tally["wars_lost"] += 1
            payout_tally["main_0x"] += 1
            show_popup("House Wins War!", "0", f"{get_card_name(house_cards[i])} beats {get_card_name(player_cards[i])}",
                       player_cards=player_cards, house_cards=house_cards, reveal_level=3-i, winner="house", card_index=i, multiplier=0)
            return 0
        else:
            show_popup("War Tie", "0", f"{get_card_name(player_cards[i])} equals {get_card_name(house_cards[i])}",
                       player_cards=player_cards, house_cards=house_cards, reveal_level=3-i, tie=True, card_index=i, multiplier=0)
            time.sleep(0.3)

    # If all three are ties, JACKPOT!
    payout = main_bet * 100
    multiplier = payout / total_bet if total_bet else None
    chip_pile += payout
    payout_tally["main_100x"] += 1
    show_popup("JACKPOT! Triple War Tie!", f"{payout}", "All three cards matched!",
               player_cards=player_cards, house_cards=house_cards, reveal_level=3, tie=True, card_index=0, multiplier=multiplier)
    return payout

def draw_war_cards(player_cards, house_cards, reveal_level=0):
    screen.blit(table_image, (0, 0))
    total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_width) // 2
    for i in range(3):
        pos_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
        pos_y_player = SCREEN_HEIGHT - CARD_HEIGHT - 50
        pos_y_house = 50
        # Player
        if player_cards[i] == 'XX':
            screen.blit(card_back, (pos_x, pos_y_player))
        else:
            screen.blit(card_images[player_cards[i]], (pos_x, pos_y_player))
        # House
        if house_cards[i] == 'XX':
            screen.blit(card_back, (pos_x, pos_y_house))
        else:
            screen.blit(card_images[house_cards[i]], (pos_x, pos_y_house))
    draw_tally()
    draw_bets_bottom()
    draw_auto_button()
    draw_profit_loss()
    pygame.display.flip()
def run_game():
    global auto_bet, auto_hands
    running = True
    auto_hands = 0
    clock = pygame.time.Clock()
    while running and chip_pile >= 50:
        if auto_bet:
            auto_hands += 1
            if auto_hands > AUTO_HANDS_MAX:
                auto_bet = False
                auto_hands = 0
                draw_table()
        else:
            auto_hands = 0

        result = play_regular_round()

        # Non-blocking delay for 1.5 seconds after round (popup already uses time.sleep)
        delay_ms = 1500
        delay_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - delay_start < delay_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    auto_bet = False
                    auto_hands = 0
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if auto_button["rect"].collidepoint(mouse_pos):
                        auto_bet = not auto_bet
                        auto_hands = 0
                        draw_table()
            draw_table()
            clock.tick(60)  # ~60 FPS

        if not running:
            break

        # Non-blocking delay for 1 second between rounds
        delay_ms = 1000
        delay_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - delay_start < delay_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    auto_bet = False
                    auto_hands = 0
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if auto_button["rect"].collidepoint(mouse_pos):
                        auto_bet = not auto_bet
                        auto_hands = 0
                        draw_table()
            draw_table()
            clock.tick(60)

    if chip_pile < 50:
        screen.blit(table_image, (0, 0))
        draw_centered_text("Game Over: Insufficient Chips!", font_large, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, (255, 0, 0))
        draw_tally()
        draw_bets_bottom()
        draw_auto_button()
        draw_profit_loss()
        pygame.display.flip()
        # Non-blocking delay for 3 seconds
        delay_ms = 3000
        delay_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - delay_start < delay_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    run_game()