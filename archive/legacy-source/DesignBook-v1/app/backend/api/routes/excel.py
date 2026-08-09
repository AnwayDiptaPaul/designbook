"""API routes — Excel manager (parse, enhance, export design sheets)."""

import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.config import get_settings
from backend.core.excel.processor import ExcelProcessor

router = APIRouter(prefix="/excel", tags=["Excel Manager"])
settings = get_settings()

def get_excel_processor():
    return ExcelProcessor(
        excel_dir=settings.DESIGN_EXCEL_DIR,
        enhanced_dir=settings.ENHANCED_EXCEL_DIR
    )

class ExcelSheetInfo(BaseModel):
    filename: str
    size_bytes: int
    category: str = "Uncategorized"

@router.get("/sheets", response_model=dict)
async def list_design_sheets(processor: ExcelProcessor = Depends(get_excel_processor)):
    """List all available design Excel files."""
    try:
        sheets = processor.list_available_sheets()
        return {"sheets": sheets, "count": len(sheets)}
    except FileNotFoundError:
        return {"sheets": [], "count": 0}

@router.post("/enhance/{filename}")
async def enhance_sheet(filename: str, processor: ExcelProcessor = Depends(get_excel_processor)):
    """Enhance a specific spreadsheet (unprotect, safely unmerge)."""
    try:
        enhanced_path = processor.enhance_sheet(filename)
        return {"status": "success", "enhanced_file": enhanced_path}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mapping/{filename}")
async def get_sheet_summary(filename: str, processor: ExcelProcessor = Depends(get_excel_processor)):
    """Extract inputs and outputs mapping out of the sheet."""
    try:
        mapping = processor.extract_inputs_outputs(filename)
        return mapping
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

