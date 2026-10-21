import dature

from koloagent.infrastructure.config.models import Config


def load_config(config_path: str) -> Config:
    return dature.load(dature.Toml10Source(file=config_path), schema=Config)
