# ===============================
# app/routes/credit_config_routes.py — With Universal Logging
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.credit_config_schema import (
    CreditConfigCreate,
    CreditConfigUpdate,
    CreditConfigResponse,
)
from app.controllers import credit_config_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error
from app.db.models.credit_model import LifecycleStatus
router = APIRouter(prefix="/credit-configs", tags=["Credit Configs"])




# ============================================================
# 🔹 GET ALL CREDIT CONFIGS
# ============================================================


@router.get("/credit-list")
async def get_active_credit_packs(db: Session = Depends(get_db)):
    """
    Public route for users — fetches only active credit packs.
    """
    try:
        packs = credit_config_controller.get_all_credit_configs(db)
        active = [p for p in packs if p.status == LifecycleStatus.active]

        # ✅ Manual serialization fix
        serialized = []
        for p in active:
            serialized.append({
                "creditid": p.creditid,
                "config_key": p.config_key,
                "config_value": p.config_value,
                "description": p.description,
                "stripe_link": p.config_value.get("stripe_price_id") if p.config_value else None,  # ✅ add this line
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            })

        print(f"✅ Returning {len(serialized)} active packs")
        return serialized
    except Exception as e:
        print(f"❌ Error fetching active credit packs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[CreditConfigResponse])
async def get_all_credit_configs(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CREDIT_PACK", request)
        result = credit_config_controller.get_all_credit_configs(db)

        await log_action(
            db, request, current_user,
            "CREDIT_PACK_LIST_VIEW",
            details="Viewed all credit packs"
        )
        return result

    except Exception as e:
        await log_error(db, request, current_user, "CREDIT_PACK_LIST_ERROR", e, "Error viewing credit packs")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET SINGLE CREDIT PACK
# ============================================================
@router.get("/{creditid}", response_model=CreditConfigResponse)
async def get_credit_config(
    creditid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CREDIT_PACK", request)
        config = credit_config_controller.get_credit_config_by_id(creditid, db)

        await log_action(
            db, request, current_user,
            "CREDIT_PACK_VIEW",
            details=f"Viewed credit pack ID: {creditid}",
            dedupe_key=f"creditpack_{creditid}"
        )
        return config

    except HTTPException as e:
        await log_error(db, request, current_user, "CREDIT_PACK_VIEW_FAILED", e, f"Failed to view pack {creditid}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CREDIT_PACK_VIEW_ERROR", e, f"Error viewing pack {creditid}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 CREATE CREDIT PACK
# ============================================================
@router.post("/", response_model=CreditConfigResponse, status_code=201)
async def create_credit_config(
    config: CreditConfigCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CREDIT_PACK", request)
        result = credit_config_controller.create_credit_config(config, db)

        await log_action(
            db, request, current_user,
            "CREDIT_PACK_CREATE",
            details=f"Created credit pack '{config.config_key}'"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "CREDIT_PACK_CREATE_FAILED", e, "Failed to create credit pack")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CREDIT_PACK_CREATE_ERROR", e, "Error creating credit pack")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 UPDATE CREDIT PACK
# ============================================================
@router.put("/{creditid}", response_model=CreditConfigResponse)
async def update_credit_config(
    creditid: int,
    config: CreditConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CREDIT_PACK", request)
        old_data = credit_config_controller.get_credit_config_by_id(creditid, db)
        result = credit_config_controller.update_credit_config(creditid, config, db)

        await log_action(
            db, request, current_user,
            "CREDIT_PACK_UPDATE",
            details=f"Updated credit pack {old_data.config_key}"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "CREDIT_PACK_UPDATE_FAILED", e, f"Failed to update pack {creditid}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CREDIT_PACK_UPDATE_ERROR", e, f"Error updating pack {creditid}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 DELETE CREDIT PACK
# ============================================================
@router.delete("/{creditid}")
async def delete_credit_config(
    creditid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CREDIT_PACK", request)
        credit_config_controller.delete_credit_config(creditid, db)

        await log_action(
            db, request, current_user,
            "CREDIT_PACK_DELETE",
            details=f"Deleted credit pack ID {creditid}"
        )
        return {"message": f"Credit pack {creditid} deleted successfully"}

    except HTTPException as e:
        await log_error(db, request, current_user, "CREDIT_PACK_DELETE_FAILED", e, f"Failed to delete pack {creditid}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CREDIT_PACK_DELETE_ERROR", e, f"Error deleting pack {creditid}")
        raise HTTPException(status_code=500, detail="Internal server error")
