# pyre-ignore-all-errors
"""Excel reference-file endpoints with safe path handling and explicit gates."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.config import get_settings
from backend.core.excel.processor import ExcelProcessor

router = APIRouter(prefix="/excel", tags=["Excel Manager"])
settings = get_settings()


def get_excel_processor():
    return ExcelProcessor(
        excel_dir=settings.resolve_path(settings.DESIGN_EXCEL_DIR),
        enhanced_dir=settings.resolve_path(settings.ENHANCED_EXCEL_DIR),
    )


class ExcelSheetInfo(BaseModel):
    filename: str
    size_bytes: int
    category: str = "Uncategorized"


def _safe_filename(filename: str) -> str:
    candidate = Path(filename)
    if candidate.name != filename or candidate.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise HTTPException(status_code=400, detail="Only a simple .xlsx or .xlsm filename is allowed")
    return filename


@router.get("/sheets", response_model=dict)
async def list_design_sheets(processor: ExcelProcessor = Depends(get_excel_processor)):
    """List retained reference workbooks; this does not execute calculations."""

    try:
        sheets = processor.list_available_sheets()
        return {"sheets": sheets, "count": len(sheets)}
    except FileNotFoundError:
        return {"sheets": [], "count": 0}


@router.post("/enhance/{filename}")
async def enhance_sheet(filename: str, processor: ExcelProcessor = Depends(get_excel_processor)):
    filename = _safe_filename(filename)
    try:
        enhanced_path = processor.enhance_sheet(filename)
        return {"status": "success", "enhanced_file": enhanced_path}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Workbook could not be safely enhanced") from exc


@router.get("/mapping/{filename}")
async def get_sheet_summary(filename: str):
    _safe_filename(filename)
    raise HTTPException(status_code=501, detail="Workbook input/output mapping is not released; no mapping was generated")