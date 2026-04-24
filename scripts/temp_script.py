import os

base_dir = r"c:\Users\HP\Downloads\DeciFlow AI\backend\app"
interfaces_dir = os.path.join(base_dir, "domain", "interfaces")
services_dir = os.path.join(base_dir, "services")

os.makedirs(interfaces_dir, exist_ok=True)
os.makedirs(services_dir, exist_ok=True)

interfaces = {
    "data_service": "from abc import ABC, abstractmethod\nfrom typing import Any, Dict\n\nclass IDataService(ABC):\n    @abstractmethod\n    def process_raw_data(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:\n        pass\n",
    "feature_service": "from abc import ABC, abstractmethod\nfrom typing import Any, Dict\n\nclass IFeatureService(ABC):\n    @abstractmethod\n    def extract_features(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:\n        pass\n",
    "insight_service": "from abc import ABC, abstractmethod\nfrom typing import Any, Dict\n\nclass IInsightService(ABC):\n    @abstractmethod\n    def generate_insights(self, features: Dict[str, Any]) -> Dict[str, Any]:\n        pass\n",
    "prediction_service": "from abc import ABC, abstractmethod\nfrom typing import Any, Dict\n\nclass IPredictionService(ABC):\n    @abstractmethod\n    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:\n        pass\n",
    "agent_service": "from abc import ABC, abstractmethod\nfrom typing import Any, Dict\n\nclass IAgentService(ABC):\n    @abstractmethod\n    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:\n        pass\n",
    "decision_service": "from abc import ABC, abstractmethod\nfrom typing import Any, Dict\n\nclass IDecisionService(ABC):\n    @abstractmethod\n    def orchestrate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:\n        pass\n"
}

for name, content in interfaces.items():
    with open(os.path.join(interfaces_dir, f"{name}.py"), "w", encoding="utf-8") as f:
        f.write(content)

with open(os.path.join(services_dir, "__init__.py"), "w", encoding="utf-8") as f:
    f.write("")

services = {
    "data_service": "from typing import Any, Dict\nfrom app.domain.interfaces.data_service import IDataService\n\nclass DataService(IDataService):\n    def process_raw_data(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:\n        return {\"status\": \"processed\", \"data\": payload}\n",
    "feature_service": "from typing import Any, Dict\nfrom app.domain.interfaces.feature_service import IFeatureService\n\nclass FeatureService(IFeatureService):\n    def extract_features(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:\n        return {\"extracted_features\": True, **processed_data}\n",
    "insight_service": "from typing import Any, Dict\nfrom app.domain.interfaces.insight_service import IInsightService\n\nclass InsightService(IInsightService):\n    def generate_insights(self, features: Dict[str, Any]) -> Dict[str, Any]:\n        return {\"insights_summary\": \"looks good\", \"features_used\": features}\n",
    "prediction_service": "from typing import Any, Dict\nfrom app.domain.interfaces.prediction_service import IPredictionService\n\nclass PredictionService(IPredictionService):\n    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:\n        return {\"prediction_score\": 0.95}\n",
    "agent_service": "from typing import Any, Dict\nfrom app.domain.interfaces.agent_service import IAgentService\n\nclass AgentService(IAgentService):\n    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:\n        return {\"agent_response\": f\"Agent {agent_name} executed successfully\"}\n",
    "decision_service": "from typing import Any, Dict\nfrom app.domain.interfaces.decision_service import IDecisionService\nfrom app.domain.interfaces.data_service import IDataService\nfrom app.domain.interfaces.feature_service import IFeatureService\nfrom app.domain.interfaces.insight_service import IInsightService\nfrom app.domain.interfaces.prediction_service import IPredictionService\n\nclass DecisionService(IDecisionService):\n    def __init__(\n        self,\n        data_service: IDataService,\n        feature_service: IFeatureService,\n        insight_service: IInsightService,\n        prediction_service: IPredictionService\n    ):\n        self._data_service = data_service\n        self._feature_service = feature_service\n        self._insight_service = insight_service\n        self._prediction_service = prediction_service\n\n    def orchestrate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:\n        processed_data = self._data_service.process_raw_data(source=\"api\", payload=context)\n        features = self._feature_service.extract_features(processed_data)\n        insights = self._insight_service.generate_insights(features)\n        predictions = self._prediction_service.predict(features)\n        decision = {\n            \"recommended_action\": \"APPROVE\",\n            \"confidence_score\": predictions.get(\"prediction_score\", 0.0),\n            \"insights\": insights\n        }\n        return decision\n"
}

for name, content in services.items():
    with open(os.path.join(services_dir, f"{name}.py"), "w", encoding="utf-8") as f:
        f.write(content)

print("Interfaces and Services generated!")
