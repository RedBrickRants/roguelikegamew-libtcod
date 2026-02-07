# Project Overview

This is a roguelike game built with Python, tcod, and pygame. The game features a modular body system where characters have body parts that can be modified, an action point system for turn-based combat, procedurally generated dungeon floors, and both melee and ranged combat systems.

## Current State

The game is functional and playable. Core systems include:

- Procedurally generated dungeon floors with rooms, corridors, and doors
- Turn-based combat with action points (AP)
- Body modification system allowing internal, external, and intrinsic modifications to body parts
- Equipment system supporting weapons and armor that can be equipped to specific body parts
- Ranged weapons with ammunition, reload mechanics, and piercing capabilities
- Enemy AI with pathfinding and line-of-sight tracking
- Experience and leveling system
- Inventory management
- Field of view and fog of war
- Message log system
- Sound effects using pygame mixer

## Known Issues and Bugs

- Action point system has bugs where the player can run out of AP unexpectedly
- Code architecture is complex and tightly coupled, making debugging difficult
- Equipment slot management for multi-slot items (like two-handed weapons) needs refinement
- Save/load system may have issues with non-pickleable objects
- Door interaction occasionally causes AP consumption inconsistencies
- Enemy modification spawning may result in imbalanced encounters

## Required Modules

- tcod
- pygame (or pygame-ce)
- numpy
- dill (for save/load serialization)
- lzma (built-in)

Install dependencies:
```
pip install tcod pygame numpy dill
```

## Running the Game

```
python main.py
```

## Controls

- Arrow keys / numpad / vi keys: Movement
- g: Pick up items
- i: Open inventory
- d: Drop items
- c: Character screen
- f: Fire ranged weapon
- r: Reload weapon
- o: Open/close door
- s: Look mode
- .: Wait
- Shift + >: Take stairs down
- ESC / q: Quit

## Development Notes

The codebase has grown organically and would benefit from refactoring. The concept and core mechanics are solid, but the implementation has become difficult to maintain. Consider this a functional prototype that demonstrates the game systems but needs architectural cleanup for long-term development.
