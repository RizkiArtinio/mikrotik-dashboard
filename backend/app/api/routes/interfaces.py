from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_router_or_404
from app.db.session import get_db
from app.models.interface import Interface
from app.models.router import Router
from app.schemas.interface import InterfaceOut

router = APIRouter(prefix="/routers", tags=["interfaces"])


@router.get("/{router_id}/interfaces", response_model=list[InterfaceOut])
async def list_interfaces(
    router_obj: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)
) -> list[Interface]:
    result = await db.execute(
        select(Interface).where(Interface.router_id == router_obj.id).order_by(Interface.interface_name)
    )
    return list(result.scalars().all())
