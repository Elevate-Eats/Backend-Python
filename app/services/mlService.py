from app.repositories.mlRepository import MLRepository
from app.utilities.predictTransaction import prediction
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MLService:
  def __init__(self):
    self.mlRepository = MLRepository()
    
  async def generateTransactionPrediction(self, branchId: int, startDate: str, endDate: str):
    dataFixForecastHelper1, dataFixForecastHelper2, dataFixForecastShift1, dataFixForecastShift2 = await self.mlRepository.fetchData(branchId, startDate, endDate)
    #logging.info(f"after repo: {dataFixForecastShift1}")
    #logging.info(f"after repo: {dataFixForecastHelper2}")

    predictionData = await prediction.predictTransaction(dataFixForecastHelper1, dataFixForecastHelper2, dataFixForecastShift1, dataFixForecastShift2)
    return predictionData
  