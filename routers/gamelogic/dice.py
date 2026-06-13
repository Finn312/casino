import random

def roll_dice():
  return random.randint(1,6)

def roll_all_dice(num_dice=2):
  combinded_dice = 0
  numbers_rolled = []
  for i in range(num_dice):
    rolled_dice = roll_dice()
    numbers_rolled.append(rolled_dice)
    combinded_dice += rolled_dice
  return combinded_dice, numbers_rolled

def calculate_win( bet, predection, num_dice=2):
  total, numbers = roll_all_dice(num_dice)
  multiplier = num_dice + 1
  if total == predection:
    return bet * multiplier, numbers
  return 0, numbers