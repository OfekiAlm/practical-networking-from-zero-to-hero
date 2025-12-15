"""Demo listing and information endpoints."""
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from backend.demos.registry import get_registry
from backend.schemas.base import DemoRecipe

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[DemoRecipe])
async def list_demos():
    """
    List all available demo recipes.
    
    Returns a list of all registered demos with their metadata,
    including parameter schemas.
    """
    try:
        registry = get_registry()
        demos = registry.list_demos()
        logger.info(f"Listed {len(demos)} available demos")
        return demos
    except Exception as e:
        logger.error(f"Error listing demos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list demos"
        )


@router.get("/{demo_id}", response_model=DemoRecipe)
async def get_demo(demo_id: str):
    """
    Get detailed information about a specific demo.
    
    Args:
        demo_id: The unique identifier of the demo
        
    Returns:
        Demo recipe with full metadata and parameter schema
    """
    try:
        registry = get_registry()
        recipe = registry.get_recipe(demo_id)
        
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demo '{demo_id}' not found"
            )
        
        logger.info(f"Retrieved demo: {demo_id}")
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demo {demo_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get demo information"
        )
