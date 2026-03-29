from sentence_transformers import SentenceTransformer
from lumina_brain.config.settings import settings


class EmbeddingService:
    """Service for handling vector embeddings"""
    
    def __init__(self):
        self.model = SentenceTransformer(
            settings.model.name,
            cache_folder=settings.model.cache_dir
        )
        print(f"Model loaded: {settings.model.name}")
    
    def encode(self, text: str) -> list:
        """Generate vector embedding from text"""
        return self.model.encode(text).tolist()


# Create global embedding service instance
embedding_service = EmbeddingService()