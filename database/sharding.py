from typing import Dict
from sqlalchemy import create_engine

class ShardManager:
    def __init__(self):
        self.shards: Dict[str, object] = {}
        self._initialize_shards()
    
    def _initialize_shards(self):
        # Configura shards baseados em ranges de CPF
        ranges = [
            ("00000000000", "19999999999"),
            ("20000000000", "39999999999"),
            ("40000000000", "59999999999"),
            ("60000000000", "79999999999"),
            ("80000000000", "99999999999")
        ]
        
        for i, (start, end) in enumerate(ranges):
            db_url = f"sqlite:///path/to/shard_{i}.db"
            self.shards[f"shard_{i}"] = {
                "engine": create_engine(db_url),
                "range": (start, end)
            }
    
    def get_shard(self, cpf: str):
        for shard_name, shard_info in self.shards.items():
            if shard_info["range"][0] <= cpf <= shard_info["range"][1]:
                return shard_info["engine"]
        raise ValueError("Shard não encontrado") 