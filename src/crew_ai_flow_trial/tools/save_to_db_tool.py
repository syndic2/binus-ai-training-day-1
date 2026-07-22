from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import mysql.connector

class SaveToDbToolInput(BaseModel):
    """Input schema for SaveToDb."""

    head: int = Field(..., description="Data jumlah deteksi head.")
    helmet: int = Field(..., description="Data jumlah deteksi helmet.")
    person: int = Field(..., description="Data jumlah deteksi person.")

class SaveToDbTool(BaseTool):
    name: str = "SaveToDbTool"
    description: str = "Clear description for what this tool is useful for, your agent will need this information to use it."
    args_schema: Type[BaseModel] = SaveToDbToolInput

    def _run(self, head: int, helmet: int, person: int) -> dict:
        try:
            connector = mysql.connector.connect(
                host = '127.0.0.1',
                user = 'jonathan',
                password = 'password_kamu',
                database = 'safety_report'
            )
            cursor = connector.cursor()

            report_result = f'{head} head, {helmet} helmet, {person} person'
            print(f"DEBUG: SaveToDbTool called with: {report_result}")
            query = 'INSERT INTO helmet_report (report_result, report_detected) VALUES (%s, %s)'
            cursor.execute(query, (report_result, head))
            connector.commit()

            cursor.close()
            connector.close()

            return {
                'head': head,
                'helmet': helmet,
                'person': person,
                'message': 'stored to db' if (head > 0) else 'everybody is in safety' 
            }
        except Exception as e:
            return {
                'head': head,
                'helmet': helmet,
                'person': person,
                'message': f'failed to store to db: {str(e)}'
            }