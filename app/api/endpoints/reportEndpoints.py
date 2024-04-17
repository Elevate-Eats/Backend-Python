from fastapi import APIRouter, Depends, HTTPException, Response, Header
from app.services.reportService import ReportService as ReportServiceClass
from fastapi.responses import StreamingResponse
import io
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
def verifyApiKey(apikey:str = Header(...)):
  if apikey !=  os.getenv("API_KEY"):
    raise HTTPException(status_code= 401, detail="Unauthorized")

def get_report_service():
  return ReportServiceClass()

@router.get("/generate-daily-report/", dependencies=[Depends(verifyApiKey)], response_class=Response, responses={
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
