import os
from pathlib import Path
os.environ['CAMPUS_DB']=str(Path(__file__).parent/'test.db')
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def register(u='student_test'):
 return client.post('/auth/register',json={'username':u,'password':'password123','name':'测试学生','role':'student','college':'计算机学院','major':'软件工程','grade':'大一'})
def auth(u='student_test'):
 r=client.post('/auth/login',json={'username':u,'password':'password123'}); return {'Authorization':'Bearer '+r.json()['access_token']}
def test_health_and_registration():
 assert client.get('/health').json()['status']=='ok'; assert register().status_code in {200,409}; assert client.post('/auth/login',json={'username':'student_test','password':'password123'}).status_code==200
def test_onboarding_required_then_recommendations():
 h=auth(); r=client.get('/recommendations',headers=h); assert r.status_code==200
 if r.json().get('onboarding_required'):
  assert client.post('/onboarding/interests',headers=h,json={'module_ids':[1,2]}).status_code==422
  assert client.post('/onboarding/interests',headers=h,json={'module_ids':[1,2,3]}).status_code==200
 assert client.get('/recommendations',headers=h).json()['items']
def test_grade_targeting_and_rag():
 u='senior_test'; assert register(u).status_code in {200,409}; h=auth(u); assert client.post('/onboarding/interests',headers=h,json={'module_ids':[9,10,6]}).status_code==200; assert len(client.get('/recommendations',headers=h).json()['items']) > 0; assert client.post('/rag/ask',headers=h,json={'question':'就业实习'}).status_code==200

