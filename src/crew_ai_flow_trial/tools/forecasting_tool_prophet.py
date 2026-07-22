from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
from prophet import Prophet
import os

class ForecastingToolProphetInput(BaseModel):
    file: str = Field(..., description="Path file Excel (.xlsx/.xls)")

class ForecastingToolProphet(BaseTool):
    name: str = "ForecastingToolProphet"
    description: str = "Forecasting data time-series dari Excel menggunakan Prophet"
    args_schema: Type[BaseModel] = ForecastingToolProphetInput

    def _run(self, file: str) -> dict:
        # =====================
        # LOAD EXCEL
        # =====================
        if not os.path.exists(file):
            raise ValueError(f"File tidak ditemukan: {file}")

        try:
            df = pd.read_excel(file, sheet_name=0)
        except Exception as e:
            raise ValueError(f"Gagal membaca Excel: {str(e)}")

        if df.empty:
            raise ValueError("Data kosong")

        # =====================
        # CLEANING
        # =====================
        df = df.iloc[:, 1:]  # buang index kolom pertama kalau ada

        for col in df.select_dtypes(include=['object']).columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna()

        if len(df) < 10:
            raise ValueError("Data terlalu sedikit")

        # =====================
        # TIME COLUMN
        # =====================
        if 'time' not in df.columns:
            raise ValueError("Kolom 'time' tidak ditemukan")

        df['ds'] = pd.to_datetime(df['time'])

        # =====================
        # TARGET COLUMN (smart pick)
        # =====================
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        priority_cols = [col for col in numeric_cols if "Temp" in col]

        if priority_cols:
            target_col = priority_cols[0]
        else:
            target_col = numeric_cols[0]

        df['y'] = df[target_col]
        df = df[['ds', 'y']].sort_values('ds')

        # =====================
        # MODEL PROPHET
        # =====================
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True
        )
        model.fit(df)

        # =====================
        # FORECAST
        # =====================
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # =====================
        # ANOMALY DETECTION (simple residual)
        # =====================
        merged = pd.merge(df, forecast[['ds', 'yhat']], on='ds', how='left')
        merged['anomaly_score'] = abs(merged['y'] - merged['yhat'])

        threshold = merged['anomaly_score'].mean() + 3 * merged['anomaly_score'].std()
        merged['is_anomaly'] = merged['anomaly_score'] > threshold

        anomaly_count = int(merged['is_anomaly'].sum())

        # =====================
        # OUTPUT
        # =====================
        
        forecast_data = (
            forecast[['ds', 'yhat']]
            .tail(10)
            .assign(ds=lambda x: x['ds'].astype(str))
            .to_dict(orient='records')
        )

        return {
            "total_data": int(len(df)),
            "anomaly_count": anomaly_count,
            "anomaly_threshold": float(threshold),
            "forecast": forecast_data
        }