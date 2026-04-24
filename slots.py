import random

Symbols = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣"]

def spin_reels ():
  return[random.choice(Symbols) for _ in range(3)]

def calculate_win(reels, bet):
  if reels[0] == reels[1] == reels[2]:
    if reels[0] == "💎":
      return bet * 25
    return bet * 10
  if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
    return bet * 2
  return 0
  
