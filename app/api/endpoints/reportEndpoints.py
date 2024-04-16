from fastapi import APIRouter, Depends, HTTPException
from app.services.reportService import ReportService as ReportServiceClass

router = APIRouter()

def get_report_service():
    return ReportServiceClass()

@router.post("/generate-daily-report/")
async def generateDailyReport(branchId: int, reportService: ReportServiceClass = Depends(get_report_service)):
  try:
    result = await reportService.generateDailyReport(branchId)
    return {"message": "Report generated succesfully", "data":result}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))