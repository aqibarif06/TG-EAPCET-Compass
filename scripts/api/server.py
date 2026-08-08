from pathlib import Path
from typing import List, Optional
import math

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scripts.predictors.cutoff_predictor import CutoffPredictor


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "csv"


# ============================================================
# PREDICTOR
# ============================================================

predictor = CutoffPredictor(DATA_DIR)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="TG-EAPCET Compass API",
    description=(
        "College recommendation API based on "
        "historical TG EAPCET cutoff data."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PredictionRequest(BaseModel):
    rank: int = Field(
        ...,
        gt=0,
        description="Student's TG EAPCET rank",
    )

    category: str = Field(
        ...,
        min_length=1,
        description="Admission category, e.g. OC_BOYS",
    )

    branches: Optional[List[str]] = Field(
        default=None,
        description="Optional branch codes such as CSE, CSM, ECE",
    )

    districts: Optional[List[str]] = Field(
        default=None,
        description="Optional district codes such as HYD, RR",
    )

    collegeTypes: Optional[List[str]] = Field(
        default=None,
        description="Optional college types: PVT, GOV, UNIV",
    )

    limit: Optional[int] = Field(
        default=20,
        gt=0,
        le=100,
        description="Maximum number of recommendations",
    )


# ============================================================
# RESPONSE HELPERS
# ============================================================

def clean_value(value, key=None):
    """
    Convert pandas/numpy values into JSON-safe Python values.

    Handles:
    - numpy scalar values
    - pandas NaN
    - positive/negative infinity
    - prediction field rounding
    """

    if value is None:
        return None

    # Handle pandas NaN / NaT
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    # Convert numpy scalar -> native Python type
    try:
        if hasattr(value, "item"):
            value = value.item()
    except Exception:
        pass

    # Handle float values
    if isinstance(value, float):

        # JSON does not allow NaN / Infinity
        if not math.isfinite(value):
            return None

        # Prediction fields
        if key == "predicted_cutoff":
            return round(value, 1)

        if key == "rank_ratio":
            return round(value, 3)

        if key == "rank_margin":
            return round(value, 1)

        # Other floating-point values
        return round(value, 4)

    return value


def dataframe_to_records(dataframe):
    """
    Convert a pandas DataFrame into JSON-safe records.
    """

    if dataframe is None or dataframe.empty:
        return []

    records = dataframe.to_dict(orient="records")

    cleaned = []

    for record in records:
        cleaned_record = {}

        for key, value in record.items():
            cleaned_record[key] = clean_value(value, key)

        cleaned.append(cleaned_record)

    return cleaned


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "name": "TG-EAPCET Compass API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "tg-eapcet-compass",
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/api/predict")
def predict(request: PredictionRequest):

    try:
        category = request.category.strip().upper()

        # Normalize optional filters
        branches = (
            [branch.strip().upper() for branch in request.branches]
            if request.branches
            else None
        )

        districts = (
            [district.strip().upper() for district in request.districts]
            if request.districts
            else None
        )

        college_types = (
            [college_type.strip().upper()
             for college_type in request.collegeTypes]
            if request.collegeTypes
            else None
        )

        result = predictor.recommendations(
            student_rank=request.rank,
            category=category,
            limit=request.limit,
            branches=branches,
            districts=districts,
            college_types=college_types,
        )

        return {
            "success": True,
            "rank": request.rank,
            "category": category,
            "count": len(result),
            "results": dataframe_to_records(result),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        )


# ============================================================
# AVAILABLE COLLEGES
# ============================================================

@app.get("/api/colleges")
def colleges():

    try:
        data = predictor.colleges.copy()

        return {
            "success": True,
            "count": len(data),
            "colleges": dataframe_to_records(data),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load colleges: {str(exc)}",
        )


# ============================================================
# AVAILABLE BRANCHES
# ============================================================

@app.get("/api/branches")
def branches():

    try:
        # Get unique branch codes and names.
        #
        # The branches.csv file contains one row per
        # college + branch combination, so we must
        # remove duplicate branch codes before sending
        # them to the frontend.

        data = (
            predictor.branches[
                ["branchCode", "branchName"]
            ]
            .copy()
        )

        # Clean values
        data["branchCode"] = (
            data["branchCode"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        data["branchName"] = (
            data["branchName"]
            .astype(str)
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # One branch code should appear only once.
        data = (
            data
            .drop_duplicates(
                subset=["branchCode"]
            )
            .sort_values(
                "branchCode"
            )
            .reset_index(drop=True)
        )

        return {
            "success": True,
            "count": len(data),
            "branches": dataframe_to_records(data),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load branches: {str(exc)}",
        )


# ============================================================
# AVAILABLE CATEGORIES
# ============================================================

@app.get("/api/categories")
def categories():

    try:
        data = (
            predictor.cutoffs["category"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        return {
            "success": True,
            "count": len(data),
            "categories": data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load categories: {str(exc)}",
        )


# ============================================================
# AVAILABLE DISTRICTS
# ============================================================

@app.get("/api/districts")
def districts():

    try:
        data = (
            predictor.colleges["district"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        return {
            "success": True,
            "count": len(data),
            "districts": data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load districts: {str(exc)}",
        )


# ============================================================
# AVAILABLE COLLEGE TYPES
# ============================================================

@app.get("/api/college-types")
def college_types():

    try:
        data = (
            predictor.colleges["collegeType"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        return {
            "success": True,
            "count": len(data),
            "collegeTypes": data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load college types: {str(exc)}",
        )