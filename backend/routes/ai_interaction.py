from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from ..core.database import get_session
from ..models.user import User
from ..services import ai_service
# Import dependency to get current user later
# from ..core.security import get_current_active_user

# Placeholder for current user dependency (reuse from campaigns for now)
def get_current_active_user_placeholder():
    class MockUser:
        id = 1 # Assume user ID 1 for now
        is_active = True
        plan_id = 1 # Assume plan ID 1
    return MockUser()

router = APIRouter()

class AIChatRequest(BaseModel):
    query: str

class AIChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=AIChatResponse)
def handle_ai_chat(
    *, 
    db: Session = Depends(get_session), 
    request: AIChatRequest,
    current_user: User = Depends(get_current_active_user_placeholder) # Replace with real dependency
):
    """
    Handles a chat interaction with the AI for the current user.
    Retrieves context from user's training data and gets a response from the AI model.
    """
    # Add check: Does user plan allow AI interaction? (Maybe based on usage limits?)
    # user_with_plan = user_service.get_user_with_plan(db, user_id=current_user.id)
    # if not user_with_plan or not user_with_plan.plan or not user_with_plan.plan.allow_ai_training: # Or a specific AI interaction flag
    #     raise HTTPException(status_code=403, detail="User plan does not allow AI interaction.")

    if not request.query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    ai_response_text = ai_service.get_ai_response(db=db, user_query=request.query, owner_id=current_user.id)
    
    return AIChatResponse(response=ai_response_text)

