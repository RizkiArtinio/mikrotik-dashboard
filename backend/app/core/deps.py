from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.router import Router


async def get_router_or_404(router_id: int, db: AsyncSession = Depends(get_db)) -> Router:
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if router is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Router {router_id} not found")
    return router
