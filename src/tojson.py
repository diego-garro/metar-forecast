def to_json(station: str, json: str):
    f = open(f"data/json/{station}.json", "w")
    f.write(json)
    f.close()
