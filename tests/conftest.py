import pytest
from app.core.config import load_settings
from app.database.db import Base, make_database
from app.database.repository import Repository
from app.detectors.responder import IncidentResponder
from app.detectors.engine import DetectionEngine

@pytest.fixture
def test_runtime(tmp_path):
    settings=load_settings()
    settings.raw["monitoring"]["watch_paths"]= [str(tmp_path/"sandbox")]
    settings.raw["response"]["quarantine_dir"]=str(tmp_path/"quarantine")
    settings.raw["reports"]["directory"]=str(tmp_path/"reports")
    engine, session=make_database("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    repo=Repository(session); responder=IncidentResponder(settings,repo); detector=DetectionEngine(settings,repo,responder)
    return settings, repo, detector
