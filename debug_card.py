from codomyrmex.data_visualization import Card
import sys

print(f"Card source: {Card}")
card = Card(title="Users", content="100")
try:
    s = str(card)
    print(f"str(card): {s}")
    if "Users" in s:
        print("PASS")
    else:
        print("FAIL: 'Users' not in string")
except Exception as e:
    print(f"ERROR: {e}")
