from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-5.6-luna"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_timeout_seconds: float = Field(default=45.0, gt=0)
    dataset_path: Path = Path("data/movies.csv")
    embedding_cache_dir: Path = Path("backend/.cache/embeddings")
    frontend_origin: str = "http://localhost:3100"
    chunk_size_words: int = Field(default=300, ge=50)
    chunk_overlap_words: int = Field(default=50, ge=0)
    embedding_batch_size: int = Field(default=64, ge=1, le=2048)

    def resolve_from(self, root: Path) -> Settings:
        update: dict[str, Path] = {}
        if not self.dataset_path.is_absolute():
            update["dataset_path"] = root / self.dataset_path
        if not self.embedding_cache_dir.is_absolute():
            update["embedding_cache_dir"] = root / self.embedding_cache_dir
        return self.model_copy(update=update)


@lru_cache
def get_settings() -> Settings:
    root = Path(__file__).resolve().parents[2]
    return Settings().resolve_from(root)
