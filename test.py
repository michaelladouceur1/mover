mover1 = [
    {
    "change": 0.15,
    "description": "string",
    "direction": "'up' or 'down'",
    "last": 0,
    "symbol": "string",
    "totalVolume": 0
    },
    {
    "change": 0.3,
    "description": "string",
    "direction": "'up' or 'down'",
    "last": 0,
    "symbol": "string",
    "totalVolume": 0
    },
]

mover2 = [
    {
    "change": 0.23,
    "description": "string",
    "direction": "'up' or 'down'",
    "last": 0,
    "symbol": "string",
    "totalVolume": 0
    },
    {
    "change": 0.1,
    "description": "string",
    "direction": "'up' or 'down'",
    "last": 0,
    "symbol": "string",
    "totalVolume": 0
    },
]

mover1.extend(mover2)
mover = sorted(mover1, key=lambda k: k['change'], reverse=True)
print(mover)