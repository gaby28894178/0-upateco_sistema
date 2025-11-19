from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from ..docs_pdf import generate_srs_pdf


router = APIRouter(prefix="/docs", tags=["docs"])


@router.get("/srs.pdf")
def srs_pdf():
    out_path = os.path.join(os.getcwd(), "docs", "SRS_ElTata.pdf")
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        generate_srs_pdf(out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return FileResponse(out_path, media_type="application/pdf", filename="SRS_ElTata.pdf")