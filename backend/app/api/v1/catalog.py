"""Public service and package catalog."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import PackageOffering, ServiceOffering
from app.schemas.care_schema import PackageOfferingDetail, ServiceOfferingDetail

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


@router.get("/services", response_model=list[ServiceOfferingDetail])
def services(db: Session = Depends(get_db)):
    return list(db.scalars(select(ServiceOffering).where(
        ServiceOffering.is_active.is_(True)
    ).order_by(ServiceOffering.price_minor.asc())).all())


@router.get("/packages", response_model=list[PackageOfferingDetail])
def packages(db: Session = Depends(get_db)):
    return list(db.scalars(select(PackageOffering).where(
        PackageOffering.is_active.is_(True)
    ).order_by(PackageOffering.price_minor.asc())).all())

