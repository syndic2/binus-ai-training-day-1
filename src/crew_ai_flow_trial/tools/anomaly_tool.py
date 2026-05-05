from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyToolInput(BaseModel):
    file: str = Field(..., description="Ini adalah input tool anomali.")

class AnomalyTool(BaseTool):
    name: str = "Tool untuk deteksi anomali data excel"
    description: str = "Untuk deteksi anomali data excel"
    args_schema: Type[BaseModel] = AnomalyToolInput

    def _run(self, file: str) -> str:
        # Implementation goes here
        data_frame = pd.read_excel(file, sheet_name=0)
        data_frame = data_frame.iloc[:, 1:]

        for col in data_frame.select_dtypes(include=['object']).columns:
            data_frame[col] = pd.to_numeric(data_frame[col], errors='coerce')

        cleaned_data_frame = data_frame.dropna()
        cleaned_data_frame['day_number'] = (cleaned_data_frame['time'] - pd.Timestamp('2000-01-01')).dt.days
        
        fixed_data_frame = cleaned_data_frame.iloc[:,1:]

        iso_forest = IsolationForest(
            contamination=0.05,
            random_state=40,
            n_estimators=100,
        )
        iso_forest.fit(fixed_data_frame)

        fixed_data_frame['anomaly_score'] = iso_forest.predict(fixed_data_frame)
        anomaly_count = (fixed_data_frame['anomaly_score'] == -1).sum()
        total_data = len(fixed_data_frame)

        return {
            'total_data': total_data,
            'anomaly_count': anomaly_count
        }
            