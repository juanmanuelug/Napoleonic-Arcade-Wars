# Napoleonic-Arcade-Wars
First project in python.   It is a 2D arcade action game develop in python using the library pygame. We are in the battle of Waterloo in the skin of an English soldier and we must finish with the hordes of French soldiers who want to bring Napoleon back to the throne.

- In the music folder, it is needed to decompress de zip

## Controls:
- left arrow: move left
- up arrow: move up
- down arrow: move down
- right arrow: move right
- space: open fire
- E: bayonet thrust (hits what is right in front of you, hurts more than a shot)
- shift: dash backwards (jumps away from the direction you are facing, to get out of a sabre that is already coming)
- Q: use what you carry in your backpack
- ESC: pause (press ESC twice to abandon the battle)
- ENTER: confirm in the menus
- 1 / 2 / 3: choose your upgrade when you are promoted

## Test mode

Reaching wave 8 to see a boss is a toll, so there is a test mode. **It is currently ON**, and a
line at the bottom right says so while it is. Turn it off either way:

```
PRUEBAS=0 python main.py     # without touching the code
MODO_PRUEBAS = False         # in main.py
```

Worth turning off before showing the game to anyone: these keys drop bosses and make you
invulnerable, and one stray `I` leaves the game pointless.

A normal game is unchanged - wave 1, recruit's musket. To jump into a wave:

```
OLEADA=8 python main.py
```

That starts at wave 8 with every upgrade and the top rank, because that is what you would have on
arriving there: with a recruit's musket a 2400-life boss is two and a half minutes of shooting,
which tests nothing.

Keys, only in test mode:

- `J`: drop a boss in the field, right now, whatever the wave. Which one is set by
  `JEFE_DE_PRUEBAS` in main.py - put there the boss you are working on. Set it to `None`
  and the key cycles through the whole wheel instead, one boss per press
- `N`: clear the field and the wave's quota, so the game moves on to the next wave
- `I`: toggle invulnerability, to watch attack patterns without dying
- `F`: drop the boss's life to its next phase, to see all three without fighting the whole fight

## Imagenes
### Main screen
![image](https://user-images.githubusercontent.com/74183704/112736268-ba8f2b80-8f51-11eb-9393-3b56ccdbc51c.png)
### Game
![image](https://user-images.githubusercontent.com/74183704/112736304-1063d380-8f52-11eb-9ea5-8963d516c10b.png)
### Game over screen
![image](https://user-images.githubusercontent.com/74183704/112736330-32f5ec80-8f52-11eb-8c66-e1c11b8deb78.png)
