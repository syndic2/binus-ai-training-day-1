from tasks.celery_app import celery_app

from src.crew_ai_flow_trial.crews.content_crew.content_crew import ContentCrew
from src.crew_ai_flow_trial.crews.analisator.analisator import Analisator
from src.crew_ai_flow_trial.crews.tax_researcher.tax_researcher import TaxResearcher
from src.crew_ai_flow_trial.crews.tax_advisor.tax_advisor import TaxAdvisor
from src.crew_ai_flow_trial.crews.file_analyzer.file_analyzer import FileAnalyzer
from src.crew_ai_flow_trial.crews.anomaly_detector.anomaly_detector import AnomalyDetector
from src.crew_ai_flow_trial.crews.forecaster.forecaster import Forecaster
from src.crew_ai_flow_trial.crews.safety_detector.safety_detector import SafetyDetector

import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='research')
def run_research(self, topic: str, audience: str):
    self.update_state(
        state='RUNNING', 
        meta={
            'current': f'start job for {topic} - {audience}'
        }
    )

    try:
        result =  ContentCrew().crew().kickoff(inputs={
            'topic': topic,
            'audience': audience
        })
        return str(result)
    except Exception as e:
        return str(e)
    
@celery_app.task(bind=True, name='market_research')
def run_market_research(self, topic: str, current_year: str):
    self.update_state(
        state='RUNNING', 
        meta={
            'current': f'start job for {topic} - {current_year}'
        }
    )

    try:
        result =  Analisator().crew().kickoff(inputs={
            'topic': topic,
            'current_year': current_year
        })
        return str(result)
    except Exception as e:
        return str(e)
    
@celery_app.task(bind=True, name='tax_research')
def run_tax_research(self, country: str, year: str):
    self.update_state(
        state='RUNNING', 
        meta={
            'current': f'start job for {country}'
        }
    )

    try:
        result =  TaxResearcher().crew().kickoff(inputs={
            'country': country,
            'year': year
        })
        return str(result)
    except Exception as e:
        return str(e)
    
@celery_app.task(bind=True, name='tax_advise')
def run_tax_advise(self, country: str, year: str):
    self.update_state(
        state='RUNNING', 
        meta={
            'current': f'start job for {country}'
        }
    )

    try:
        result =  TaxAdvisor().crew().kickoff(inputs={
            'country': country,
            'year': year
        })
        return str(result)
    except Exception as e:
        return str(e)

@celery_app.task(bind=True, name='file_text_analyzer')
def run_file_text_analyzer(self, file: str):
    self.update_state(
        state='RUNNING', 
        meta={
            'current': f'start job for {file}'
        }
    )

    try:
        result =  FileAnalyzer().crew().kickoff(inputs={
            'file': file
        })
        return result.json_dict
    except Exception as e:
        return str(e)

@celery_app.task(bind=True, name='anomaly_detection')
def run_anomaly_detection(self, file: str):
    self.update_state(
        state='RUNNING', 
        meta={
            'current': f'start detecting anomaly using prophet for {file}'
        }
    )

    try:
        result =  AnomalyDetector().crew().kickoff(inputs={
            'file': file
        })
        return result.json_dict
    except Exception as e:
        return str(e)

@celery_app.task(bind=True, name='forecasting')
def run_forecasting(self, file: str):
    import json
    import ast

    self.update_state(
        state='RUNNING', 
        meta={'current': f'start forecasting for {file}'}
    )

    try:
        result = Forecaster().crew().kickoff(inputs={'file': file})
        
        # =====================
        # HANDLE OUTPUT
        # =====================
        if hasattr(result, "json_dict") and result.json_dict:
            clean = result.json_dict

        elif hasattr(result, "raw"):
            raw = result.raw.strip()

            if raw.startswith("```"):
                raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                clean = json.loads(raw)
            except:
                clean = {"raw": raw}
        else:
            clean = {"result": str(result)}

        # 🔥 FIX: convert forecast string → list
        if isinstance(clean.get("forecast"), str):
            try:
                clean["forecast"] = ast.literal_eval(clean["forecast"])
            except:
                pass

        # 🔥 force JSON safe
        return json.loads(json.dumps(clean))
    except Exception as e:
        return str(e)

@celery_app.task(bind=True, name='helmet_detection')
def run_helmet_detection(self, image: str):
    self.update_state(
        state='RUNNING', 
        meta={'current': f'start helmet detection for {image}'}
    )

    try:
        result = SafetyDetector().crew().kickoff(
            inputs={
                'image': image
            }
        )
        
        if hasattr(result, "json_dict") and result.json_dict:
            return result.json_dict

        if hasattr(result, "raw"):
            import json
            raw = result.raw.strip()

            if raw.startswith("```"):
                raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                return json.loads(raw)
            except:
                return {"raw": raw}

        return {"result": str(result)}
    except Exception as e:
        return str(e)   