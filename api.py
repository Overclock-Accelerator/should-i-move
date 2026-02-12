"""
FastAPI server for Should I Move? agent system.
Provides REST API endpoints to trigger move analysis.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict
import uvicorn
import os
import glob
from datetime import datetime
from dotenv import load_dotenv

# Import agent coordinator
from agno_coordinator import analyze_move_non_interactive, save_report
from sub_agents.schemas import UserProfile, FinalRecommendation

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Should I Move? API",
    description="AI-powered multi-agent system to help decide if you should move to a new city",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results (use a database in production)
analysis_results: Dict[str, dict] = {}


class AnalysisRequest(BaseModel):
    """Request model for move analysis"""
    current_city: str = Field(..., description="The city you currently live in", example="New York City")
    desired_city: str = Field(..., description="The city you're considering moving to", example="Austin")
    annual_income: Optional[float] = Field(None, description="Your annual income", example=85000.0)
    monthly_expenses: Optional[float] = Field(None, description="Your monthly expenses", example=3500.0)
    city_preferences: list[str] = Field(
        default_factory=list,
        description="What you value in a city",
        example=["good weather", "tech industry", "arts scene"]
    )
    current_city_likes: list[str] = Field(
        default_factory=list,
        description="What you like about your current city",
        example=["great public transit", "diverse food options"]
    )
    current_city_dislikes: list[str] = Field(
        default_factory=list,
        description="What you dislike about your current city",
        example=["high cost of living", "harsh winters"]
    )


class AnalysisResponse(BaseModel):
    """Response model for analysis initiation"""
    analysis_id: str = Field(..., description="Unique ID for tracking this analysis")
    status: str = Field(..., description="Status of the analysis request")
    message: str = Field(..., description="Human-readable message")
    estimated_completion_time: str = Field(..., description="Estimated time to complete")


class AnalysisStatus(BaseModel):
    """Response model for analysis status check"""
    analysis_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    result: Optional[FinalRecommendation] = None
    error: Optional[str] = None


def run_analysis(analysis_id: str, user_profile: UserProfile):
    """Background task to run the agent analysis"""
    try:
        # Update status to processing
        analysis_results[analysis_id]["status"] = "processing"
        analysis_results[analysis_id]["message"] = "Analysis in progress..."
        
        # Run the analysis
        recommendation = analyze_move_non_interactive(user_profile)
        
        # Save the report
        save_report(user_profile, recommendation)
        
        # Update with results
        analysis_results[analysis_id]["status"] = "completed"
        analysis_results[analysis_id]["message"] = "Analysis completed successfully"
        analysis_results[analysis_id]["result"] = recommendation
        analysis_results[analysis_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        # Update with error
        analysis_results[analysis_id]["status"] = "failed"
        analysis_results[analysis_id]["message"] = "Analysis failed"
        analysis_results[analysis_id]["error"] = str(e)
        analysis_results[analysis_id]["completed_at"] = datetime.now().isoformat()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Should I Move? API",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Submit a move analysis request",
            "GET /analysis/{analysis_id}": "Check analysis status and get results",
            "GET /report/{analysis_id}": "Retrieve the markdown report for a completed analysis"
        }
    }


@app.get("/health")
async def health_check():
    """Health check for deployment monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/analyze", response_model=AnalysisResponse, status_code=202)
async def analyze_move(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a move analysis request.
    
    This endpoint initiates an asynchronous analysis using multiple AI agents.
    Returns an analysis_id that can be used to check the status and retrieve results.
    """
    # Validate required fields
    if not request.current_city or not request.desired_city:
        raise HTTPException(
            status_code=400,
            detail="current_city and desired_city are required fields"
        )
    
    # Generate unique analysis ID
    analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Convert request to UserProfile
    user_profile = UserProfile(
        current_city=request.current_city,
        desired_city=request.desired_city,
        annual_income=request.annual_income,
        monthly_expenses=request.monthly_expenses,
        city_preferences=request.city_preferences,
        current_city_likes=request.current_city_likes,
        current_city_dislikes=request.current_city_dislikes
    )
    
    # Store initial status
    analysis_results[analysis_id] = {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Analysis queued for processing",
        "user_profile": user_profile.model_dump(),
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    # Add background task
    background_tasks.add_task(run_analysis, analysis_id, user_profile)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="pending",
        message="Analysis request received and queued for processing",
        estimated_completion_time="2-5 minutes"
    )


@app.get("/analysis/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """
    Check the status of an analysis request and retrieve results if completed.
    
    Returns:
    - status: "pending", "processing", "completed", or "failed"
    - result: FinalRecommendation object if status is "completed"
    - error: Error message if status is "failed"
    """
    if analysis_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID '{analysis_id}' not found"
        )
    
    analysis_data = analysis_results[analysis_id]
    
    return AnalysisStatus(
        analysis_id=analysis_data["analysis_id"],
        status=analysis_data["status"],
        message=analysis_data["message"],
        result=analysis_data.get("result"),
        error=analysis_data.get("error")
    )


@app.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Delete an analysis record from memory.
    Useful for cleanup after retrieving results.
    """
    if analysis_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID '{analysis_id}' not found"
        )
    
    del analysis_results[analysis_id]
    
    return {
        "message": f"Analysis '{analysis_id}' deleted successfully",
        "deleted_at": datetime.now().isoformat()
    }


@app.get("/report/{analysis_id}", response_class=PlainTextResponse)
async def get_report_markdown(analysis_id: str):
    """
    Retrieve the markdown report for a completed analysis.
    
    Args:
        analysis_id: The analysis ID (e.g., analysis_20260212_001510_934692)
    
    Returns:
        The full markdown report as plain text
    
    Example:
        GET /report/analysis_20260212_001510_934692
    """
    # Extract timestamp from analysis_id (format: analysis_YYYYMMDD_HHMMSS_microseconds)
    # We need YYYYMMDD_HHMMSS part for matching the report filename
    if not analysis_id.startswith("analysis_"):
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis_id format. Expected format: analysis_YYYYMMDD_HHMMSS_microseconds"
        )
    
    # Extract timestamp portion (without microseconds)
    # analysis_20260212_001510_934692 -> 20260212_001510
    timestamp_parts = analysis_id.replace("analysis_", "").split("_")
    if len(timestamp_parts) < 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis_id format"
        )
    
    timestamp = f"{timestamp_parts[0]}_{timestamp_parts[1]}"  # YYYYMMDD_HHMMSS
    
    # Search for report file matching the timestamp
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        raise HTTPException(
            status_code=404,
            detail="Reports directory not found. No reports have been generated yet."
        )
    
    # Find files matching the timestamp pattern
    pattern = os.path.join(reports_dir, f"*_{timestamp}_analysis.md")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail=f"Report not found for analysis_id: {analysis_id}. The analysis may still be processing or may have failed."
        )
    
    # If multiple matches (unlikely), use the first one
    report_file = matching_files[0]
    
    # Read and return the markdown content
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading report file: {str(e)}"
        )


if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )
