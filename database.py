"""
database.py - MongoDB connectivity and operations for AI Resume Analyzer
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import streamlit as st

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "resume_analyzer")


def get_db_client():
    """Create and return a MongoDB client with connection pooling via Streamlit cache."""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        st.error(f"❌ MongoDB Connection Failed: {e}")
        return None


def get_database():
    """Get the database instance."""
    client = get_db_client()
    if client:
        return client[MONGODB_DB_NAME]
    return None


def save_resume_analysis(
    filename: str,
    resume_text: str,
    analysis: dict,
    job_description: str = None
) -> str | None:
    """
    Save resume and its AI analysis to MongoDB.
    Returns the inserted document ID as string, or None on failure.
    """
    db = get_database()
    if db is None:
        return None

    collection = db["resumes"]
    document = {
        "filename": filename,
        "resume_text": resume_text,
        "job_description": job_description,
        "analysis": analysis,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        st.error(f"❌ Failed to save to MongoDB: {e}")
        return None


def get_all_analyses(limit: int = 50) -> list:
    """
    Retrieve all saved resume analyses, newest first.
    Returns a list of documents.
    """
    db = get_database()
    if db is None:
        return []

    collection = db["resumes"]
    try:
        documents = list(
            collection.find(
                {},
                {"resume_text": 0}  # Exclude raw text for performance
            ).sort("created_at", DESCENDING).limit(limit)
        )
        # Convert ObjectId to string for display
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return documents
    except Exception as e:
        st.error(f"❌ Failed to fetch analyses: {e}")
        return []


def get_analysis_by_id(doc_id: str) -> dict | None:
    """Fetch a single resume analysis by its MongoDB ObjectId string."""
    from bson import ObjectId

    db = get_database()
    if db is None:
        return None

    collection = db["resumes"]
    try:
        doc = collection.find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        st.error(f"❌ Failed to fetch document: {e}")
        return None


def delete_analysis(doc_id: str) -> bool:
    """Delete a resume analysis document by ID."""
    from bson import ObjectId

    db = get_database()
    if db is None:
        return False

    collection = db["resumes"]
    try:
        result = collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0
    except Exception as e:
        st.error(f"❌ Failed to delete document: {e}")
        return False


def get_stats() -> dict:
    """Get aggregate statistics from the database."""
    db = get_database()
    if db is None:
        return {}

    collection = db["resumes"]
    try:
        total = collection.count_documents({})
        pipeline = [
            {"$group": {"_id": None, "avg_score": {"$avg": "$analysis.overall_score"}}},
        ]
        avg_result = list(collection.aggregate(pipeline))
        avg_score = round(avg_result[0]["avg_score"], 1) if avg_result else 0

        return {
            "total_resumes": total,
            "avg_score": avg_score,
        }
    except Exception as e:
        return {"total_resumes": 0, "avg_score": 0}


def check_connection() -> bool:
    """Check if MongoDB is reachable. Returns True/False."""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False
