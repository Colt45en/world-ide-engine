"""
World Engine API Service
Provides RESTful endpoints for semantic analysis and lexicon processing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os

from scales.seeds import SeedManager, DEFAULT_SEEDS, DEFAULT_CONSTRAINTS
from context.parser import TextParser


class AnalysisRequest(BaseModel):
    """Request model for text analysis."""
    text: str


class SeedRequest(BaseModel):
    """Request model for adding seeds."""
    word: str
    value: float


class AnalysisResponse(BaseModel):
    """Response model for text analysis."""
    text: str
    tokens: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    sentences: List[str]
    sentiment_score: Optional[float] = None
    keywords: List[str]


class WorldEngineAPI:
    """Core API handler for World Engine."""
    
    def __init__(self):
        # Determine seeds persistence file (allow override using SEEDS_FILE env var)
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        os.makedirs(config_dir, exist_ok=True)
        # default to sqlite for production durability; still supports .json as legacy
        default_seed_file = os.path.join(config_dir, "seeds.db")
        self.seed_file = os.environ.get("SEEDS_FILE", default_seed_file)

        self.seed_manager = SeedManager()
        self.text_parser = TextParser()

        # If a persisted seed file exists load it (JSON or SQLite), otherwise load defaults and persist them
        loaded = False
        # If using DB ensure migrations are applied early
        if self.seed_file.endswith('.db'):
            try:
                from scales.migrations import run_migrations
                run_migrations(self.seed_file)
            except Exception:
                pass
        try:
            if self.seed_file.endswith('.db'):
                loaded = self.seed_manager.load_from_db(self.seed_file)
            else:
                loaded = self.seed_manager.load_from_file(self.seed_file)
        except Exception:
            loaded = False

        if not loaded:
            self.seed_manager.load_defaults()
            try:
                if self.seed_file.endswith('.db'):
                    self.seed_manager.save_to_db(self.seed_file)
                else:
                    self.seed_manager.save_to_file(self.seed_file)
            except Exception:
                # best effort - don't fail initialization on save errors
                pass
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text with semantic scoring.
        
        Combines:
        - Seed lookup
        - Contextual analysis
        - Constraint validation
        """
        parsed = self.text_parser.parse(text)
        keywords = self.text_parser.extract_keywords(text)
        
        # Calculate sentiment score from seeds
        sentiment_scores = []
        for token in parsed["tokens"]:
            lemma = token["lemma"].lower()
            seed_value = self.seed_manager.get_seed(lemma)
            if seed_value is not None:
                # Context-sensitive scoring based on syntactic role
                if token["dep"] == "neg":  # Negation
                    sentiment_scores.append(-seed_value)
                else:
                    sentiment_scores.append(seed_value)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        return {
            "text": text,
            "tokens": parsed["tokens"],
            "entities": parsed["entities"],
            "sentences": parsed["sentences"],
            "sentiment_score": avg_sentiment,
            "keywords": keywords,
        }


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="World Engine API",
        description="Lexicon processing and semantic analysis system",
        version="1.0.0",
    )
    
    # Initialize API
    engine = WorldEngineAPI()
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Redirect to studio interface."""
        return """
        <html>
            <head>
                <meta http-equiv="refresh" content="0; url=/web/studio.html" />
            </head>
            <body>
                <p>Redirecting to <a href="/web/studio.html">Studio Interface</a>...</p>
            </body>
        </html>
        """
    
    @app.post("/api/analyze", response_model=AnalysisResponse)
    async def analyze_text(request: AnalysisRequest):
        """Analyze text for semantic content."""
        try:
            result = engine.analyze_text(request.text)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/seeds")
    async def add_seed(request: SeedRequest):
        """Add a new semantic seed word."""
        try:
            engine.seed_manager.add_seed(request.word, request.value)
            # Persist the updated seeds to disk (best-effort)
            try:
                if engine.seed_file.endswith('.db'):
                    engine.seed_manager.save_to_db(engine.seed_file)
                else:
                    engine.seed_manager.save_to_file(engine.seed_file)
            except Exception:
                pass
            return {"status": "success", "word": request.word, "value": request.value}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/seeds")
    async def get_seeds():
        """Get all current seed words."""
        return {"seeds": engine.seed_manager.seeds}
    
    @app.get("/api/constraints/validate")
    async def validate_constraints():
        """Validate all semantic constraints."""
        violations = engine.seed_manager.validate_constraints()
        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    @app.put("/api/seeds/{word}")
    async def update_seed(word: str, request: SeedRequest):
        """Update an existing seed's value (or create if missing)."""
        try:
            engine.seed_manager.add_seed(word, request.value)
            try:
                if engine.seed_file.endswith('.db'):
                    engine.seed_manager.save_to_db(engine.seed_file)
                else:
                    engine.seed_manager.save_to_file(engine.seed_file)
            except Exception:
                pass
            return {"status": "success", "word": word, "value": request.value}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/api/seeds/{word}")
    async def delete_seed(word: str):
        """Delete seed word from the store."""
        deleted = engine.seed_manager.delete_seed(word)
        if deleted:
            try:
                if engine.seed_file.endswith('.db'):
                    engine.seed_manager.save_to_db(engine.seed_file)
                else:
                    engine.seed_manager.save_to_file(engine.seed_file)
            except Exception:
                pass
            return {"status": "deleted", "word": word}
        raise HTTPException(status_code=404, detail="Seed not found")

    @app.post("/api/constraints")
    async def add_constraint(item: dict):
        """Add a constraint (word1, operator, word2) via JSON body."""
        w1 = item.get('word1')
        op = item.get('operator')
        w2 = item.get('word2')
        if not (w1 and op and w2):
            raise HTTPException(status_code=400, detail='word1, operator and word2 required')
        try:
            engine.seed_manager.add_constraint(w1, op, w2)
            try:
                if engine.seed_file.endswith('.db'):
                    engine.seed_manager.save_to_db(engine.seed_file)
                else:
                    engine.seed_manager.save_to_file(engine.seed_file)
            except Exception:
                pass
            return {"status": "success", "constraint": [w1, op, w2]}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/api/constraints")
    async def delete_constraint(item: dict):
        """Delete a constraint via JSON body (word1, operator, word2)."""
        w1 = item.get('word1')
        op = item.get('operator')
        w2 = item.get('word2')
        if not (w1 and op and w2):
            raise HTTPException(status_code=400, detail='word1, operator and word2 required')
        deleted = engine.seed_manager.delete_constraint(w1, op, w2)
        if deleted:
            try:
                if engine.seed_file.endswith('.db'):
                    engine.seed_manager.save_to_db(engine.seed_file)
                else:
                    engine.seed_manager.save_to_file(engine.seed_file)
            except Exception:
                pass
            return {"status": "deleted", "constraint": [w1, op, w2]}
        raise HTTPException(status_code=404, detail='constraint not found')

    @app.get("/api/constraints")
    async def list_constraints():
        """List all constraints."""
        return {"constraints": engine.seed_manager.constraints}

    @app.get("/api/health")
    async def health():
        """Health endpoint for readiness checks."""
        return {"status": "ok"}
    
    # Mount web directory for static files
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
    if os.path.exists(web_dir):
        app.mount("/web", StaticFiles(directory=web_dir), name="web")
    
    return app
