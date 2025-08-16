from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.schemas.query import QueryRequest, QueryResponse
from app.models.user import User

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    🌾 **Ask Agricultural Question**
    
    **Example:**
    ```
    {
        "query": "What is the best time to plant wheat in Punjab?"
    }
    ```
    """
    
    # Mock response for now
    mock_response = f"""
    Based on your location ({current_user.state_name}):
    
    🌾 **Agricultural Advice for your question:** "{query_request.query}"
    
    **Recommendations:**
    - This is a demo response
    - Personalized for {current_user.state_name} region
    - In production, this will use AI models
    
    **Next Steps:**
    - Monitor weather conditions
    - Consult local experts
    - Follow best practices for your region
    """
    
    return QueryResponse(
        answer=mock_response,
        confidence=0.8,
        sources=["Demo Database", "Mock Response"],
        processing_time=0.5,
        user_location=current_user.state_name
    )
