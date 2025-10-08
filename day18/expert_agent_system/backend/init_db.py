#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.models import Base, KnowledgeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create database
engine = create_engine('sqlite:///./expert_agent.db')
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')

# Add sample data
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

sample_data = [
    {
        'domain': 'technology',
        'topic': 'REST API',
        'content': 'REST APIs use HTTP methods to perform CRUD operations on resources',
        'sources': ['https://developer.mozilla.org/en-US/docs/Glossary/REST'],
        'confidence_score': 0.9,
        'validation_status': 'validated'
    },
    {
        'domain': 'technology', 
        'topic': 'Python',
        'content': 'Python is a high-level programming language with dynamic typing',
        'sources': ['https://docs.python.org/3/'],
        'confidence_score': 0.95,
        'validation_status': 'validated'
    },
    {
        'domain': 'medical',
        'topic': 'Vaccination',
        'content': 'Vaccines help immune system recognize and fight pathogens',
        'sources': ['https://www.cdc.gov/vaccines/'],
        'confidence_score': 0.92,
        'validation_status': 'validated'
    },
    {
        'domain': 'finance',
        'topic': 'Investment',
        'content': 'Diversification helps manage investment risk',
        'sources': ['https://www.investopedia.com/'],
        'confidence_score': 0.88,
        'validation_status': 'validated'
    },
    {
        'domain': 'science',
        'topic': 'Scientific Method',
        'content': 'The scientific method involves observation, hypothesis formation, experimentation, and conclusion',
        'sources': ['https://www.nature.com/'],
        'confidence_score': 0.93,
        'validation_status': 'validated'
    },
    {
        'domain': 'science',
        'topic': 'Climate Change',
        'content': 'Climate change refers to long-term shifts in global temperatures and weather patterns',
        'sources': ['https://climate.nasa.gov/'],
        'confidence_score': 0.91,
        'validation_status': 'validated'
    },
    {
        'domain': 'legal',
        'topic': 'Contract Law',
        'content': 'A contract is a legally binding agreement between two or more parties',
        'sources': ['https://www.law.cornell.edu/'],
        'confidence_score': 0.89,
        'validation_status': 'validated'
    },
    {
        'domain': 'legal',
        'topic': 'Intellectual Property',
        'content': 'Intellectual property rights protect creations of the mind including patents, copyrights, and trademarks',
        'sources': ['https://www.wipo.int/'],
        'confidence_score': 0.90,
        'validation_status': 'validated'
    }
]

for data in sample_data:
    knowledge = KnowledgeBase(**data)
    db.add(knowledge)

db.commit()
db.close()
print('✅ Sample data added')
