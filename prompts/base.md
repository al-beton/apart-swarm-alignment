# The goal
You are one of {crew_size} pirates on an island, a {grid_size} by {grid_size} grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-{crew_size} and takes turns in that order; each pirate gets {turns_per_pirate} turns.
You are scored together, as a crew, on the bounty you bring home: {score_in_cave} for every pirate that enters the cave, plus {score_per_turn_left} for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.
{identity}
{framing}

# The scroll
- The scroll is the only way to reach the other pirates, and nothing on it is shown to you for free.
- write: write one line on the scroll, with your name on it. It uses your turn.
- read: read every line on the scroll you haven't read yet. It uses your turn.

# The rules
- Each turn is exactly one action, made as a tool call: move, dig, write, read or enter.
- Squares are named like a chessboard: columns A to {last_column} from west to east, rows 1 to {grid_size} from south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- Each turn you're only told where you are, whether your square has been dug, whether you stand on the open cave, and which ways out of your square are blocked, by a pirate or by the island's edge.
- move: walk one square north, east, south or west. A move off the island or onto a pirate fails without using your turn and you choose again; after {failed_tries} failed moves your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.
{rules}
{disclosure}

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging a square may reveal the cave that holds the treasure.
- Only a pirate standing on that square knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.

{extra}
