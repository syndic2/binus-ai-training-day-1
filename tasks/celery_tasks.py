from tasks.celery_app import celery_app
from src.crew_ai_flow_trial.crews.content_crew.content_crew import ContentCrew
from src.crew_ai_flow_trial.crews.analisator.analisator import Analisator
from src.crew_ai_flow_trial.crews.tax_researcher.tax_researcher import TaxResearcher
from src.crew_ai_flow_trial.crews.tax_advisor.tax_advisor import TaxAdvisor

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