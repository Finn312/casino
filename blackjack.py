import random


    


def build_deck():

  SUITS = ["♠", "♥", "♦", "♣"]
  WERT = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Bube", "Dame", "König", "Ass"]
  
  deck = [f"{zeichen} {zahl}" for zahl in SUITS for zeichen in WERT]
  return deck
  
  
def shuffle_deck():
  deck = build_deck()
  random.shuffle(deck)
  return deck


def card_value(card):
  split_card = card.split(" ")
  
  zahl = split_card[0]

  if zahl in ["Bube", "Dame", "König"]:
      return 10
  elif zahl == "Ass":
      return 11
  else:
      return int(zahl)
    
def hand_value(cards):
    value = 0
    asse = 0
    for i in cards:
        v = card_value(i)
        if v == 11:
            asse += 1
        value += v
    while value > 21 and asse > 0:
        value -= 10
        asse -= 1
    return value
      
def check_winner(player_hand, dealer_hand):
    if player_hand > 21:
        return "dealer"
    if dealer_hand > 21:
        return "player"
    if player_hand == dealer_hand:
        return "draw"
    return "player" if player_hand > dealer_hand else "dealer"
  

def dealer_draw(dealer_hand, deck):
  while hand_value(dealer_hand) < 17:
    dealer_hand.append(deck.pop(0))
  return dealer_hand

  
    
    
    