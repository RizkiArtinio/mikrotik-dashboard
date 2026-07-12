import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encrypt_secret
from app.core.deps import get_router_or_404
from app.core.security import require_engineer_or_admin, require_super_admin
from app.db.session import get_db
from app.models.router import Router
from app.schemas.router import ConnectionTestResult, RouterCreate, RouterOut, RouterUpdate
from app.services.router_service import RouterCommandError, RouterConnectionError, RouterService

router = APIRouter(prefix="/routers", tags=["routers"])


@router.get("", response_model=list[RouterOut])
async def list_routers(db: AsyncSession = Depends(get_db)) -> list[Router]:
    result = await db.execute(select(Router).order_by(Router.id))
    return list(result.scalars().all())


@router.get("/{router_id}", response_model=RouterOut)
async def get_router(router: Router = Depends(get_router_or_404)) -> Router:
    return router


@router.post(
    "", response_model=RouterOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_super_admin)]
)
async def create_router(payload: RouterCreate, db: AsyncSession = Depends(get_db)) -> Router:
    router = Router(
        name=payload.name,
        ip_address=payload.ip_address,
        username=payload.username,
        password_encrypted=encrypt_secret(payload.password),
        api_port=payload.api_port,
        use_ssl=payload.use_ssl,
        site=payload.site,
        isp_gateway=payload.isp_gateway,
        wireguard_endpoint=payload.wireguard_endpoint,
    )
    db.add(router)
    await db.commit()
    await db.refresh(router)
    return router


@router.put("/{router_id}", response_model=RouterOut, dependencies=[Depends(require_super_admin)])
async def update_router(
    payload: RouterUpdate, router: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)
) -> Router:
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        password = data.pop("password")
        if password:
            router.password_encrypted = encrypt_secret(password)
    for field, value in data.items():
        setattr(router, field, value)

    await db.commit()
    await db.refresh(router)
    return router


@router.delete("/{router_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_super_admin)])
async def delete_router(router: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)) -> None:
    await db.delete(router)
    await db.commit()


@router.post(
    "/{router_id}/test-connection",
    response_model=ConnectionTestResult,
    dependencies=[Depends(require_engineer_or_admin)],
)
async def test_connection(router: Router = Depends(get_router_or_404)) -> ConnectionTestResult:
    service = RouterService(router)
    try:
        resources = await asyncio.to_thread(service.get_resources)
    except (RouterConnectionError, RouterCommandError) as exc:
        return ConnectionTestResult(success=False, message=str(exc))

    return ConnectionTestResult(
        success=True,
        message="Connected successfully",
        identity=router.name,
        routeros_version=resources.get("version"),
    )
