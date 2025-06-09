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

def draw_border(winner, cards=None, card_index=None):
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
    pygame.display.flip()
    time.sleep(0.5)

def show_popup(message, payout, result, player_cards=None, house_cards=None, reveal_level=0, winner=None, card_index=None):
    screen.blit(table_image, (0, 0))

    # Redraw cards
    if player_cards and len(player_cards) > 1:  # War round
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
    elif player_cards:  # Regular round
        screen.blit(card_images[player_cards[0]], ((SCREEN_WIDTH - CARD_WIDTH) // 2, SCREEN_HEIGHT - CARD_HEIGHT - 50))
        screen.blit(card_images[house_cards[0]], ((SCREEN_WIDTH - CARD_WIDTH) // 2, 50))

    # Redraw border if applicable
    if winner == "player":
        if card_index is not None:
            total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
            start_x = (SCREEN_WIDTH - total_width) // 2
            pos_x = start_x + card_index * (CARD_WIDTH + CARD_SPACING)
            pos_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
            pygame.draw.rect(screen, (0, 255, 0), (pos_x - 5, pos_y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
        else:
            pygame.draw.rect(screen, (0, 255, 0), ((SCREEN_WIDTH - CARD_WIDTH) // 2 - 5, SCREEN_HEIGHT - CARD_HEIGHT - 50 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
    elif winner == "house":
        if card_index is not None:
            total_width = 3 * CARD_WIDTH + 2 * CARD_SPACING
            start_x = (SCREEN_WIDTH - total_width) // 2
            pos_x = start_x + card_index * (CARD_WIDTH + CARD_SPACING)
            pos_y = 50
            pygame.draw.rect(screen, (255, 0, 0), (pos_x - 5, pos_y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)
        else:
            pygame.draw.rect(screen, (255, 0, 0), ((SCREEN_WIDTH - CARD_WIDTH) // 2 - 5, 50 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 5)

    # Draw popup
    popup = pygame.Surface((300, 150))
    popup.fill((0, 0, 0))
    pygame.draw.rect(popup, (255, 215, 0), popup.get_rect(), 5)

    color = (50, 200, 50) if "Player" in message or "Triple" in message else (200, 50, 50) if "House" in message else (255, 255, 255)
    draw_centered_text(message, font_medium, popup, 150, 40, color)
    draw_centered_text(f"{payout}x" if payout != "WAR" else "WAR", font_large, popup, 150, 80, (255, 255, 255))
    draw_centered_text(result, font_small, popup, 150, 120, (255, 255, 255))

    popup_x = (SCREEN_WIDTH - popup.get_width()) // 2
    popup_y = (SCREEN_HEIGHT - popup.get_height()) // 2
    screen.blit(popup, (popup_x, popup_y))
    pygame.display.flip()
    time.sleep(1.5)
    screen.blit(table_image, (0, 0))

def draw_table():
    screen.blit(table_image, (0, 0))
    pygame.display.flip()

def draw_single_card(card, position, face_up=True):
    x = (SCREEN_WIDTH - CARD_WIDTH) // 2
    y = SCREEN_HEIGHT - CARD_HEIGHT - 50 if position == 0 else 50
    if face_up:
        screen.blit(card_images[card], (x, y))
    else:
        screen.blit(card_back, (x, y))
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
    
    pygame.display.flip()

def create_shuffled_deck():
    deck = [v + s for v in values for s in suits.keys()]
    random.shuffle(deck)
    return deck

def play_regular_round():
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
    
    if p_val > h_val:
        draw_border("player")
        show_popup("Player Wins!", 2.0, f"{get_card_name(player_card)} beats {get_card_name(house_card)}",
                   player_cards=[player_card], house_cards=[house_card], winner="player")
        return 2.0
    elif h_val > p_val:
        draw_border("house")
        show_popup("House Wins!", 0.0, f"{get_card_name(house_card)} beats {get_card_name(player_card)}",
                   player_cards=[player_card], house_cards=[house_card], winner="house")
        return 0.0
    else:
        show_popup("Player House Tie", "WAR", f"{get_card_name(player_card)} equals {get_card_name(house_card)}",
                   player_cards=[player_card], house_cards=[house_card])
        time.sleep(1.5)
        return play_war_round(deck)

def play_war_round(deck):
    if len(deck) < 6:
        show_popup("Deck Empty", 1.0, "Starting fresh hand...", player_cards=[], house_cards=[])
        return 1.0
    
    player_cards = [deck.pop(0) for _ in range(3)]
    house_cards = [deck.pop(0) for _ in range(3)]
    
    # Initial face-down display
    draw_war_cards(player_cards, house_cards, 0)
    time.sleep(1.5)
    
    # Round 1: Reveal 3rd card (index 2)
    draw_war_cards(player_cards, house_cards, 1)
    time.sleep(1.5)
    
    p_value3 = card_value(player_cards[2])
    h_value3 = card_value(house_cards[2])
    if p_value3 > h_value3:
        draw_border("player", player_cards, 2)
        show_popup("Player Wins War!", 2.5, f"{get_card_name(player_cards[2])} beats {get_card_name(house_cards[2])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=1, winner="player", card_index=2)
        return 2.5
    elif h_value3 > p_value3:
        draw_border("house", house_cards, 2)
        show_popup("House Wins War!", 0.0, f"{get_card_name(house_cards[2])} beats {get_card_name(player_cards[2])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=1, winner="house", card_index=2)
        return 0.0
    else:
        show_popup("Player House Tie", "WAR", f"{get_card_name(player_cards[2])} equals {get_card_name(house_cards[2])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=1)
        time.sleep(1.5)
    
    # Round 2: Reveal 2nd card (index 1)
    draw_war_cards(player_cards, house_cards, 2)
    time.sleep(1.5)
    
    p_value2 = card_value(player_cards[1])
    h_value2 = card_value(house_cards[1])
    if p_value2 > h_value2:
        draw_border("player", player_cards, 1)
        show_popup("Player Wins War!", 3.5, f"{get_card_name(player_cards[1])} beats {get_card_name(house_cards[1])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=2, winner="player", card_index=1)
        return 3.5
    elif h_value2 > p_value2:
        draw_border("house", house_cards, 1)
        show_popup("House Wins War!", 0.0, f"{get_card_name(house_cards[1])} beats {get_card_name(player_cards[1])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=2, winner="house", card_index=1)
        return 0.0
    else:
        show_popup("Player House Tie", "WAR", f"{get_card_name(player_cards[1])} equals {get_card_name(house_cards[1])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=2)
        time.sleep(1.5)
    
    # Round 3: Reveal 1st card (index 0)
    draw_war_cards(player_cards, house_cards, 3)
    time.sleep(1.5)
    
    p_value1 = card_value(player_cards[0])
    h_value1 = card_value(house_cards[0])
    if p_value1 > h_value1:
        draw_border("player", player_cards, 0)
        show_popup("Player Wins War!", 5.0, f"{get_card_name(player_cards[0])} beats {get_card_name(house_cards[0])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=3, winner="player", card_index=0)
        return 5.0
    elif h_value1 > p_value1:
        draw_border("house", house_cards, 0)
        show_popup("House Wins War!", 0.0, f"{get_card_name(house_cards[0])} beats {get_card_name(player_cards[0])}",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=3, winner="house", card_index=0)
        return 0.0
    else:
        show_popup("JACKPOT! Triple Draw!", 10.0, "All three cards matched!",
                   player_cards=player_cards, house_cards=house_cards, reveal_level=3)
        return 10.0

def run_game():
    running = True
    while running:
        result = play_regular_round()
        time.sleep(1.5)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        if not running:
            break
            
        draw_table()
        time.sleep(1.0)
    
    pygame.quit()

run_game()