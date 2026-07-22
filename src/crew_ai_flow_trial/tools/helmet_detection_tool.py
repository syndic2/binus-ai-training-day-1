from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ultralytics import YOLO
from typing import Dict

class HelmetDetectionToolInput(BaseModel):
    image: str = Field(..., description="Path image")

class HelmetDetectionTool(BaseTool):
    name: str = "HelmetDetectionTool"
    description: str = "Tool untuk mendeteksi orang yang memakai helmet dan yang tidak memakai helmet"
    args_schema: Type[BaseModel] = HelmetDetectionToolInput

    model: YOLO = YOLO('src/crew_ai_flow_trial/tools/model_yolo.pt')

    def _run(self, image: str) -> Dict[str, any]:
        detection_result = self.model(image)
        detected_objects = detection_result[0].boxes.cls.tolist()
        class_names = detection_result[0].names

        head = 0
        helmet = 0
        person = 0

        for result in detected_objects:
            class_name = class_names[int(result)]

            if class_name == 'head':
                head += 1
            elif class_name == 'helmet':
                helmet += 1
            elif class_name == 'person':
                person += 1

        return {
            'head_count': head,
            'helmet_count': helmet,
            'person_count': person
        }