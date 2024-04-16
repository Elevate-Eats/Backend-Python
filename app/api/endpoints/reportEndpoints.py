from fastapi import APIRouter, Depends, HTTPException, Response
from app.services.reportService import ReportService as ReportServiceClass
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

def get_report_service():
  return ReportServiceClass()

@router.get("/generate-daily-report/", response_class=Response, responses={
  200: {
    "description": "Returns the daily report as a PDF",
    "content": {"application/pdf": {}}
  },
  500: {
    "description": "Internal Server Error"
  }
})
async def generateDailyReport(branchId: int, date: str, reportService: ReportServiceClass = Depends(get_report_service)):
  try:
    result = await reportService.generateDailyReport(branchId, date)
    return StreamingResponse(io.BytesIO(result), media_type="application/pdf")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
