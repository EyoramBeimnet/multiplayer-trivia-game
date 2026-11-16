# Multiplayer Trivia: JSON Protocol (v1)

## Wire format

- Transport: TCP, one socket per player.
- Each message is **one compact JSON object on a single line, ending in `\n`**. Pretty-printed examples below are for reading only.
- Every message has `"v"` (protocol version, currently `1`) and `"type"`.
- No player IDs. The server identifies a player by their socket, and **names are unique**.
- The **host is the first player to join**. If the host leaves, the server promotes the longest-connected remaining player.

## Messages

| Type | Direction | Fields |
|---|---|---|
| `JOIN` | client → server | `room` (str), `name` (str) |
| `JOIN_ACK` | server → client | `is_host` (bool) |
| `PLAYERS` | server → all | `players` (list of str), `host` (str) |
| `START_GAME` | host client → server | none |
| `START` | server → all | `total_questions` (int) |
| `QUESTION` | server → all | `number` (int), `text` (str), `choices` (list of str), `duration` (int, seconds) |
| `ANSWER` | client → server | `number` (int), `choice` (int, index into `choices`) |
| `QUESTION_END` | server → each client | `number` (int), `correct` (int), `counts` (list of int, one per choice), `your_choice` (int or null), `points` (int) |
| `SCORE` | server → all | `scores` (list of `{"name", "score"}`, sorted high to low) |
| `FINAL` | server → all | `scores` (same shape as SCORE) |
| `LEAVE` | client → server | none |
| `ERROR` | either | `code` (int), `message` (str) |

## Examples

```json
{
  "v": 1,
  "type": "JOIN",
  "room": "ABCD",
  "name": "Mark"
}
```

```json
{
  "v": 1,
  "type": "QUESTION",
  "number": 2,
  "text": "What does TCP stand for?",
  "choices": ["A", "B", "C", "D"],
  "duration": 15
}
```

```json
{
  "v": 1,
  "type": "QUESTION_END",
  "number": 2,
  "correct": 1,
  "counts": [0, 3, 1, 0],
  "your_choice": 1,
  "points": 840
}
```

```json
{
  "v": 1,
  "type": "SCORE",
  "scores": [
    {"name": "Mark", "score": 1520},
    {"name": "Sasha", "score": 900}
  ]
}
```

## Timer rules

1. The server sends QUESTION and records the send time.
2. Clients run a countdown **for display only** and send nothing when it hits zero.
3. The server closes the question when `duration` elapses, or earlier if every connected player has answered.
4. QUESTION_END is the only "time's up" signal. Any ANSWER arriving after it gets ERROR 8.
5. Points are computed on the server from `arrival_time - send_time`.

## Error codes

| Code | Meaning |
|---|---|
| 1 | Malformed JSON |
| 2 | Unknown type or missing field |
| 3 | Version mismatch |
| 4 | Wrong room code |
| 5 | Name already taken |
| 6 | Room full |
| 7 | Game already in progress |
| 8 | Answer too late, or for the wrong question number |
| 9 | Duplicate answer |
| 10 | Not the host |
| 11 | Message not valid in the current state |

After codes 1, 2 and 3 the server may drop the connection. After the others, the client stays connected.

## Disconnect rules

- A dead socket (`recv()` returns empty) or a LEAVE removes the player, and the server sends PLAYERS. If the player was the host, the host role passes on first.
- Mid-question, the leaver no longer counts toward "everyone has answered," and their score is dropped from later SCORE messages.
- If everyone leaves, the server resets to an empty lobby.

## Typical flow

`JOIN` → `JOIN_ACK` → `PLAYERS` → `START_GAME` → `START` → (`QUESTION` → `ANSWER`s → `QUESTION_END` → `SCORE`) × N → `FINAL`

## Still undecided

If all players but one drop mid-game, does the game continue, or does the last player get `FINAL` right away? Pick a rule and add it to the disconnect section.