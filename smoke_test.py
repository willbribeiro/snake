"""Headless smoke test for snake.py - validates the exact scenarios that crashed."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # run without a real window

import snake

g = snake.SnakeGame()

# 1. Game must START ON THE MENU, not game_over
assert g.state == 'menu', f"FAIL: started in '{g.state}' instead of 'menu'"
assert len(g.snake) == 0, "FAIL: snake populated on menu"
print("PASS 1: starts on menu, snake empty")

# 2. Menu must STAY on menu with no input (no auto-transition)
for _ in range(10):
    g.draw()
assert g.state == 'menu', f"FAIL: auto-transitioned to '{g.state}'"
print("PASS 2: menu persists without input (no instant game over)")

# 3. start_run -> playing with 3 synced segments
g.start_run()
assert g.state == 'playing', f"FAIL: state '{g.state}' after start_run"
assert len(g.snake) == 3, f"FAIL: {len(g.snake)} segments"
hx, hy = g.snake[0]
bx, by = g.snake[1]
assert bx == hx - g.snake_block and by == hy, "FAIL: body not behind head"
print("PASS 3: run starts with 3 segments, body behind head")

# 4. First movement step must NOT kill the snake (the old desync bug)
for _ in range(5):
    g._step()
    assert g.state == 'playing', f"FAIL: died on step (state={g.state})"
print("PASS 4: first 5 steps survive (no instant self-collision)")

# 5. Eating food grows the snake and scores
hx, hy = g.snake[0]
g.food = (hx + g.snake_block, hy)   # force food onto the next head cell
g._step()
assert g.score == 10, f"FAIL: score {g.score}"
assert len(g.snake) == 4, f"FAIL: length {len(g.snake)}"
print("PASS 5: eating works (+10, grew to 4)")

# 6. 180-degree reversal must be rejected (input buffering)
g.pending.append((-1, 0))           # reverse of (1,0)
g._step()
assert g.direction == (1, 0), f"FAIL: reversal accepted -> {g.direction}"
assert g.state == 'playing', "FAIL: died from reversal"
print("PASS 6: reversal rejected, snake alive")

# 7. Buffered turn chain applies over two steps (no death)
g.pending.append((0, -1))           # UP (valid from RIGHT)
g.pending.append((-1, 0))           # then LEFT (valid from UP)
g._step()
assert g.direction == (0, -1) and g.state == 'playing'
g._step()
assert g.direction == (-1, 0) and g.state == 'playing'
print("PASS 7: buffered double-turn works without death")

# 8. Wall collision eventually ends the run -> game_over state
for _ in range(400):
    if g.state != 'playing':
        break
    g._step()
assert g.state == 'game_over', f"FAIL: expected game_over, got '{g.state}'"
print("PASS 8: wall collision triggers game_over")

# 9. High score persisted
import os.path
assert g.high_score == 10 and os.path.exists('highscore.json')
print("PASS 9: high score saved (10)")

# 10. game_over -> menu -> new run works
g.handle_event(type('E', (), {'type': snake.pygame.KEYDOWN, 'key': snake.pygame.K_q})())
assert g.state == 'menu'
g.handle_event(type('E', (), {'type': snake.pygame.KEYDOWN, 'key': snake.pygame.K_RETURN})())
assert g.state == 'playing' and len(g.snake) == 3
print("PASS 10: game over -> menu -> restart works")

print("\nALL 10 SMOKE TESTS PASSED - the crash scenarios are fixed.")
