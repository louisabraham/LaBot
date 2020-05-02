from pathlib import Path
import pickle

with (Path(__file__).parent / "protocol.pk").open("rb") as f:
    types = pickle.load(f)
    msg_from_id = pickle.load(f)
    types_from_id = pickle.load(f)
    primitives = pickle.load(f)
