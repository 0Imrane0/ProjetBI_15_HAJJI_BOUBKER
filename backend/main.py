import logging
import asyncio
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from ml_engine.batch_service import batch_recommendation_service
from ml_engine.monitoring_service import monitoring_service
from ml_engine.recommendation_service import recommendation_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelStatus(BaseModel):
    ready: bool
    last_trained_at: Optional[str] = None
    training_summary: Optional[dict] = None


class TrainResponse(BaseModel):
    status: str
    model: ModelStatus


class RecommendationItem(BaseModel):
    rank: int
    report_id: int
    metabase_report_id: Optional[int] = None
    title: str
    description: str
    category: str
    business_category: str
    score: float
    algorithm: str


class RecommendationsResponse(BaseModel):
    user_id: int
    count: int
    recommendations: List[RecommendationItem]
    model: ModelStatus


class BatchGenerateResponse(BaseModel):
    batch_id: str
    generated_at: str
    requested_top_n: int
    users: int
    recommendations_inserted: int
    model: ModelStatus


class StoredRecommendationsResponse(BaseModel):
    user_id: int
    batch_id: Optional[str] = None
    count: int
    recommendations: List[dict]


app = FastAPI(
    title="BI Recommendation API",
    description="API for adaptive BI recommendation engine",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the BI Recommendation API",
        "endpoints": {
            "health": "/health",
            "train": "POST /train",
            "recommendations": "GET /recommendations/{user_id}?n=5",
            "batch_generate": "POST /batch/recommendations/generate?n=5",
            "batch_status": "GET /batch/status",
            "stored_recommendations": "GET /stored-recommendations/{user_id}?n=5",
            "monitoring": "GET /monitoring/summary",
        },
    }

@app.get("/health")
def health_check():
    model_status = recommendation_service.status()
    return {
        "status": "healthy",
        "model_ready": model_status["ready"],
        "model": model_status,
    }


@app.post("/train", response_model=TrainResponse)
def train_model():
    """
    Trigger batch training for the tuned hybrid model.
    """
    try:
        status = recommendation_service.train()
        return {"status": "trained", "model": status}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Training failed")
        raise HTTPException(status_code=500, detail="Training failed") from exc


@app.get("/recommendations/{user_id}", response_model=RecommendationsResponse)
def get_recommendations(
    user_id: int,
    n: int = Query(default=5, ge=1, le=20, description="Number of recommendations"),
):
    """
    Return top-N report recommendations for an internal user id.
    """
    try:
        recommendations = recommendation_service.recommend(
            user_id=user_id,
            n_recommendations=n,
        )
        return {
            "user_id": user_id,
            "count": len(recommendations),
            "recommendations": recommendations,
            "model": recommendation_service.status(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Recommendation request failed for user_id=%s", user_id)
        raise HTTPException(
            status_code=500,
            detail="Recommendation request failed",
        ) from exc


@app.post("/batch/recommendations/generate", response_model=BatchGenerateResponse)
def generate_batch_recommendations(
    n: int = Query(default=5, ge=1, le=20, description="Stored recommendations per user"),
):
    """
    Generate and store top-N recommendations for every user.
    """
    try:
        return batch_recommendation_service.generate_for_all_users(n_recommendations=n)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Batch recommendation generation failed")
        raise HTTPException(
            status_code=500,
            detail="Batch recommendation generation failed",
        ) from exc


@app.get("/batch/status")
def get_batch_status():
    """
    Return latest runtime and persisted batch status.
    """
    try:
        return batch_recommendation_service.status()
    except Exception as exc:
        logger.exception("Batch status request failed")
        raise HTTPException(status_code=500, detail="Batch status request failed") from exc


@app.get("/stored-recommendations/{user_id}", response_model=StoredRecommendationsResponse)
def get_stored_recommendations(
    user_id: int,
    n: int = Query(default=5, ge=1, le=20, description="Number of stored recommendations"),
):
    """
    Return latest stored top-N recommendations for one user.
    """
    try:
        return batch_recommendation_service.get_latest_for_user(
            user_id=user_id,
            n_recommendations=n,
        )
    except Exception as exc:
        logger.exception("Stored recommendation request failed for user_id=%s", user_id)
        raise HTTPException(
            status_code=500,
            detail="Stored recommendation request failed",
        ) from exc


@app.get("/monitoring/summary")
def get_monitoring_summary():
    """
    Return compact demo monitoring metrics.
    """
    try:
        return monitoring_service.summary()
    except Exception as exc:
        logger.exception("Monitoring summary request failed")
        raise HTTPException(
            status_code=500,
            detail="Monitoring summary request failed",
        ) from exc


async def _daily_batch_scheduler():
    """
    Minimal optional scheduler controlled by environment variables.
    """
    interval_seconds = int(os.getenv("BATCH_SCHEDULER_INTERVAL_SECONDS", "86400"))
    top_n = int(os.getenv("BATCH_SCHEDULER_TOP_N", "5"))
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            batch_recommendation_service.generate_for_all_users(n_recommendations=top_n)
        except Exception:
            logger.exception("Scheduled batch recommendation generation failed")


@app.on_event("startup")
async def maybe_start_batch_scheduler():
    if os.getenv("BATCH_SCHEDULER_ENABLED", "false").lower() == "true":
        asyncio.create_task(_daily_batch_scheduler())
        logger.info("Batch scheduler enabled")
