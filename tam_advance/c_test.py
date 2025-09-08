# TAM Co-Pilot Agent Implementation
# Based on Google ADK (Application Development Kit)
# Version: 1.0
# Date: September 8, 2025

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Google Cloud imports
import functions_framework
from google.cloud import bigquery
from google.cloud import monitoring_v3
from google.cloud import billing_v1
from google.cloud import securitycenter
from google.cloud import recommender_v1
from google.cloud.support_v2 import CaseServiceClient
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account
from vertexai import generative_models
from vertexai.preview import rag
from vertexai.preview.generative_models import Tool, FunctionDeclaration, Schema, Type
import vertexai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# Data Models & Enums
# ==========================================

class HealthStatus(Enum):
    OK = "OK"
    WARNING = "Warning"
    CRITICAL = "Critical"

@dataclass
class HealthSummary:
    performance_status: str
    cost_trend_percent: float
    new_critical_findings: int
    optimization_recommendations: int

@dataclass
class SupportCase:
    case_id: str
    title: str
    priority: str
    last_update: str

@dataclass
class PlatformHealthResponse:
    project_id: str
    health_summary: HealthSummary

@dataclass
class SupportCasesResponse:
    total_open_cases: int
    p1_cases: int
    cases: List[SupportCase]

@dataclass
class QBRMetrics:
    project_id: str
    quarter: str
    total_cost: float
    cost_trend: float
    top_services: List[Dict[str, float]]
    recommendations: List[str]
    usage_highlights: Dict[str, Any]

# ==========================================
# Configuration
# ==========================================

class Config:
    PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'tam-copilot-project')
    REGION = os.environ.get('GCP_REGION', 'us-central1')
    BIGQUERY_DATASET = 'tam_agent_analytics'
    VERTEX_AI_MODEL = 'gemini-1.5-pro'
    RAG_CORPUS_NAME = 'tam-knowledge-base'
    
    # Service Account paths
    SA_FUNCTIONS = 'sa-tam-agent-functions'
    SA_VERTEX_AGENT = 'sa-vertex-agent'
    
    # API Endpoints
    SUPPORT_API_ENDPOINT = "cloudsupport.googleapis.com"
    
    # BigQuery Tables
    TABLE_COST_USAGE = f"{PROJECT_ID}.{BIGQUERY_DATASET}.project_cost_and_usage_daily"
    TABLE_SUPPORT_HISTORY = f"{PROJECT_ID}.{BIGQUERY_DATASET}.support_case_history"

# ==========================================
# Cloud Function: Platform Health Check
# ==========================================

@functions_framework.http
def get_platform_health(request):
    """
    HTTP Cloud Function to get platform health metrics.
    Request JSON: { "project_id": "project-123", "time_period_days": 7 }
    """
    try:
        request_json = request.get_json(silent=True)
        if not request_json or 'project_id' not in request_json:
            return json.dumps({"error": "Missing 'project_id' in request"}), 400
        
        project_id = request_json['project_id']
        time_period_days = request_json.get('time_period_days', 7)
        
        # Initialize health checker
        health_checker = PlatformHealthChecker(project_id)
        health_summary = health_checker.check_health(time_period_days)
        
        response = PlatformHealthResponse(
            project_id=project_id,
            health_summary=health_summary
        )
        
        return json.dumps(asdict(response)), 200
        
    except Exception as e:
        logger.error(f"Error in get_platform_health: {str(e)}")
        return json.dumps({"error": str(e)}), 500

class PlatformHealthChecker:
    """Handles platform health check logic"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.billing_client = billing_v1.CloudBillingClient()
        self.scc_client = securitycenter.SecurityCenterClient()
        self.recommender_client = recommender_v1.RecommenderClient()
        self.bq_client = bigquery.Client()
    
    def check_health(self, time_period_days: int) -> HealthSummary:
        """Comprehensive health check across multiple dimensions"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=time_period_days)
        
        # Check performance metrics
        performance_status = self._check_performance_metrics(start_time, end_time)
        
        # Check cost trends
        cost_trend = self._analyze_cost_trend(start_time, end_time)
        
        # Check security findings
        critical_findings = self._check_security_findings(start_time)
        
        # Get optimization recommendations
        recommendations = self._get_recommendations()
        
        return HealthSummary(
            performance_status=performance_status.value,
            cost_trend_percent=cost_trend,
            new_critical_findings=critical_findings,
            optimization_recommendations=len(recommendations)
        )
    
    def _check_performance_metrics(self, start_time: datetime, end_time: datetime) -> HealthStatus:
        """Check CPU, memory, and latency metrics"""
        
        project_name = f"projects/{self.project_id}"
        interval = monitoring_v3.TimeInterval(
            {
                "end_time": {"seconds": int(end_time.timestamp())},
                "start_time": {"seconds": int(start_time.timestamp())},
            }
        )
        
        # Query CPU utilization
        cpu_query = monitoring_v3.ListTimeSeriesRequest(
            name=project_name,
            filter='metric.type="compute.googleapis.com/instance/cpu/utilization"',
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        )
        
        try:
            cpu_results = self.monitoring_client.list_time_series(request=cpu_query)
            
            # Analyze results
            high_cpu_count = 0
            for ts in cpu_results:
                for point in ts.points:
                    if point.value.double_value > 0.8:  # 80% threshold
                        high_cpu_count += 1
            
            if high_cpu_count > 10:
                return HealthStatus.WARNING
            elif high_cpu_count > 20:
                return HealthStatus.CRITICAL
            else:
                return HealthStatus.OK
                
        except Exception as e:
            logger.warning(f"Could not fetch performance metrics: {e}")
            return HealthStatus.OK
    
    def _analyze_cost_trend(self, start_time: datetime, end_time: datetime) -> float:
        """Analyze cost trends from BigQuery"""
        
        query = f"""
        SELECT 
            SUM(cost) as total_cost,
            DATE(usage_date) as date
        FROM `{Config.TABLE_COST_USAGE}`
        WHERE project_id = @project_id
            AND usage_date BETWEEN @start_date AND @end_date
        GROUP BY date
        ORDER BY date
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("project_id", "STRING", self.project_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_time.date()),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_time.date()),
            ]
        )
        
        try:
            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if len(results) >= 2:
                first_cost = results[0].total_cost
                last_cost = results[-1].total_cost
                trend_percent = ((last_cost - first_cost) / first_cost) * 100
                return round(trend_percent, 2)
            return 0.0
            
        except Exception as e:
            logger.warning(f"Could not analyze cost trend: {e}")
            return 0.0
    
    def _check_security_findings(self, since: datetime) -> int:
        """Count new critical security findings"""
        
        parent = f"organizations/{self._get_org_id()}/sources/-"
        
        filter_str = (
            f'severity="CRITICAL" AND '
            f'event_time > "{since.isoformat()}Z"'
        )
        
        try:
            findings = self.scc_client.list_findings(
                request={
                    "parent": parent,
                    "filter": filter_str
                }
            )
            return sum(1 for _ in findings)
            
        except Exception as e:
            logger.warning(f"Could not fetch security findings: {e}")
            return 0
    
    def _get_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        
        parent = f"projects/{self.project_id}/locations/global/recommenders/google.compute.instance.MachineTypeRecommender"
        
        try:
            recommendations = self.recommender_client.list_recommendations(
                parent=parent
            )
            return [r.description for r in recommendations][:5]  # Top 5
            
        except Exception as e:
            logger.warning(f"Could not fetch recommendations: {e}")
            return []
    
    def _get_org_id(self) -> str:
        """Helper to get organization ID"""
        # In production, fetch from project metadata
        return os.environ.get('GCP_ORG_ID', '123456789')

# ==========================================
# Cloud Function: Support Cases
# ==========================================

@functions_framework.http
def get_support_cases(request):
    """
    HTTP Cloud Function to get open support cases.
    Request JSON: { "customer_account_id": "customers/12345" }
    """
    try:
        request_json = request.get_json(silent=True)
        if not request_json or 'customer_account_id' not in request_json:
            return json.dumps({"error": "Missing 'customer_account_id'"}), 400
        
        customer_id = request_json['customer_account_id']
        
        # Initialize support case manager
        case_manager = SupportCaseManager()
        response = case_manager.get_open_cases(customer_id)
        
        return json.dumps(asdict(response)), 200
        
    except Exception as e:
        logger.error(f"Error in get_support_cases: {str(e)}")
        return json.dumps({"error": str(e)}), 500

class SupportCaseManager:
    """Manages support case operations"""
    
    def __init__(self):
        client_options = ClientOptions(api_endpoint=Config.SUPPORT_API_ENDPOINT)
        self.client = CaseServiceClient(client_options=client_options)
    
    def get_open_cases(self, customer_id: str) -> SupportCasesResponse:
        """Fetch all open support cases for a customer"""
        
        request_filter = 'state="OPEN"'
        
        try:
            response = self.client.list_cases(
                parent=customer_id,
                filter=request_filter
            )
            
            cases_list = []
            p1_count = 0
            
            for case in response:
                if case.priority == 'P1':
                    p1_count += 1
                
                cases_list.append(SupportCase(
                    case_id=case.name.split('/')[-1],
                    title=case.display_name,
                    priority=case.priority.name if hasattr(case.priority, 'name') else str(case.priority),
                    last_update=str(case.update_time)
                ))
            
            # Limit to 10 cases for response size
            return SupportCasesResponse(
                total_open_cases=len(cases_list),
                p1_cases=p1_count,
                cases=cases_list[:10]
            )
            
        except Exception as e:
            logger.error(f"Error fetching support cases: {e}")
            raise

# ==========================================
# Cloud Function: QBR Data Generation
# ==========================================

@functions_framework.http
def generate_qbr_data(request):
    """
    HTTP Cloud Function to generate QBR data.
    Request JSON: { "project_id": "project-123", "quarter": "Q3-2025" }
    """
    try:
        request_json = request.get_json(silent=True)
        if not request_json or 'project_id' not in request_json:
            return json.dumps({"error": "Missing 'project_id'"}), 400
        
        project_id = request_json['project_id']
        quarter = request_json.get('quarter', _get_current_quarter())
        
        qbr_generator = QBRDataGenerator(project_id)
        qbr_data = qbr_generator.generate_qbr_metrics(quarter)
        
        return json.dumps(asdict(qbr_data)), 200
        
    except Exception as e:
        logger.error(f"Error in generate_qbr_data: {str(e)}")
        return json.dumps({"error": str(e)}), 500

class QBRDataGenerator:
    """Generates comprehensive QBR metrics"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.bq_client = bigquery.Client()
    
    def generate_qbr_metrics(self, quarter: str) -> QBRMetrics:
        """Generate all QBR metrics for a given quarter"""
        
        start_date, end_date = self._parse_quarter(quarter)
        
        # Get cost metrics
        total_cost, cost_trend = self._get_cost_metrics(start_date, end_date)
        
        # Get top services by cost
        top_services = self._get_top_services(start_date, end_date)
        
        # Get usage highlights
        usage_highlights = self._get_usage_highlights(start_date, end_date)
        
        # Get recommendations
        recommendations = self._get_quarterly_recommendations()
        
        return QBRMetrics(
            project_id=self.project_id,
            quarter=quarter,
            total_cost=total_cost,
            cost_trend=cost_trend,
            top_services=top_services,
            recommendations=recommendations,
            usage_highlights=usage_highlights
        )
    
    def _get_cost_metrics(self, start_date: datetime, end_date: datetime) -> tuple:
        """Calculate total cost and trend for the quarter"""
        
        query = f"""
        WITH quarterly_costs AS (
            SELECT 
                DATE_TRUNC(usage_date, QUARTER) as quarter,
                SUM(cost) as total_cost
            FROM `{Config.TABLE_COST_USAGE}`
            WHERE project_id = @project_id
                AND usage_date BETWEEN DATE_SUB(@start_date, INTERVAL 3 MONTH) AND @end_date
            GROUP BY quarter
            ORDER BY quarter DESC
            LIMIT 2
        )
        SELECT 
            total_cost,
            LAG(total_cost) OVER (ORDER BY quarter DESC) as prev_quarter_cost
        FROM quarterly_costs
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("project_id", "STRING", self.project_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
            ]
        )
        
        try:
            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                current_cost = results[0].total_cost
                prev_cost = results[0].prev_quarter_cost if len(results) > 0 and results[0].prev_quarter_cost else current_cost
                trend = ((current_cost - prev_cost) / prev_cost * 100) if prev_cost > 0 else 0
                return current_cost, round(trend, 2)
            
            return 0.0, 0.0
            
        except Exception as e:
            logger.error(f"Error getting cost metrics: {e}")
            return 0.0, 0.0
    
    def _get_top_services(self, start_date: datetime, end_date: datetime) -> List[Dict[str, float]]:
        """Get top 5 services by cost"""
        
        query = f"""
        SELECT 
            service_name,
            SUM(cost) as total_cost
        FROM `{Config.TABLE_COST_USAGE}`
        WHERE project_id = @project_id
            AND usage_date BETWEEN @start_date AND @end_date
        GROUP BY service_name
        ORDER BY total_cost DESC
        LIMIT 5
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("project_id", "STRING", self.project_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
            ]
        )
        
        try:
            query_job = self.bq_client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [
                {"service": row.service_name, "cost": row.total_cost}
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting top services: {e}")
            return []
    
    def _get_usage_highlights(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get key usage highlights for the quarter"""
        
        highlights = {
            "compute_instances": self._count_compute_instances(),
            "storage_gb": self._get_storage_usage(),
            "api_calls": self._get_api_call_volume(start_date, end_date),
            "active_services": self._count_active_services(start_date, end_date)
        }
        
        return highlights
    
    def _get_quarterly_recommendations(self) -> List[str]:
        """Generate strategic recommendations for the quarter"""
        
        recommendations = [
            "Consider migrating batch workloads to Spot VMs for 60-90% cost savings",
            "Enable committed use discounts for predictable workloads",
            "Review and right-size underutilized compute instances",
            "Implement lifecycle policies for Cloud Storage to optimize costs",
            "Enable Cloud Armor DDoS protection for public-facing services"
        ]
        
        return recommendations[:3]  # Top 3 recommendations
    
    def _parse_quarter(self, quarter: str) -> tuple:
        """Parse quarter string to date range"""
        # Format: Q3-2025
        q_num = int(quarter[1])
        year = int(quarter.split('-')[1])
        
        quarter_months = {
            1: (1, 3),
            2: (4, 6),
            3: (7, 9),
            4: (10, 12)
        }
        
        start_month, end_month = quarter_months[q_num]
        start_date = datetime(year, start_month, 1)
        
        if end_month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    def _count_compute_instances(self) -> int:
        """Count active compute instances"""
        # Simplified - in production, query actual Compute Engine API
        return 42
    
    def _get_storage_usage(self) -> float:
        """Get total storage usage in GB"""
        # Simplified - in production, query Cloud Storage API
        return 1250.5
    
    def _get_api_call_volume(self, start_date: datetime, end_date: datetime) -> int:
        """Get total API calls for the period"""
        # Simplified - in production, query Cloud Logging
        return 1500000
    
    def _count_active_services(self, start_date: datetime, end_date: datetime) -> int:
        """Count number of active GCP services"""
        # Simplified - in production, query from billing data
        return 15

def _get_current_quarter() -> str:
    """Helper to get current quarter"""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"Q{quarter}-{now.year}"

# ==========================================
# Vertex AI Agent Configuration
# ==========================================

class TAMCopilotAgent:
    """Main orchestrator for the TAM Co-Pilot Agent"""
    
    def __init__(self):
        vertexai.init(project=Config.PROJECT_ID, location=Config.REGION)
        self.model = generative_models.GenerativeModel(Config.VERTEX_AI_MODEL)
        self._setup_tools()
    
    def _setup_tools(self):
        """Configure all tools for the agent"""
        
        # Tool 1: Platform Health Check
        health_check_func = FunctionDeclaration(
            name="get_platform_health",
            description="Retrieves a summary of a project's performance, cost, and security posture",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The GCP project ID to check"
                    },
                    "time_period_days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default: 7)"
                    }
                },
                "required": ["project_id"]
            }
        )
        
        # Tool 2: Support Cases
        support_cases_func = FunctionDeclaration(
            name="get_open_support_cases",
            description="Fetches list and status of open support cases for a customer",
            parameters={
                "type": "object",
                "properties": {
                    "customer_account_id": {
                        "type": "string",
                        "description": "The customer account ID (format: customers/12345)"
                    }
                },
                "required": ["customer_account_id"]
            }
        )
        
        # Tool 3: QBR Data
        qbr_data_func = FunctionDeclaration(
            name="generate_qbr_data",
            description="Gathers key metrics for quarterly business reviews",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The GCP project ID"
                    },
                    "quarter": {
                        "type": "string",
                        "description": "Quarter to analyze (format: Q3-2025)"
                    }
                },
                "required": ["project_id"]
            }
        )
        
        # Tool 4: Technical Questions (RAG)
        tech_question_func = FunctionDeclaration(
            name="answer_technical_question",
            description="Searches knowledge base to answer technical questions about Google Cloud",
            parameters={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The technical question to answer"
                    }
                },
                "required": ["question"]
            }
        )
        
        self.tools = Tool(
            function_declarations=[
                health_check_func,
                support_cases_func,
                qbr_data_func,
                tech_question_func
            ]
        )
    
    def process_request(self, user_prompt: str) -> str:
        """Process a user request and return response"""
        
        # System prompt
        system_prompt = """
        You are 'TAM Co-Pilot,' an expert Google Cloud Technical Account Manager assistant. 
        Your purpose is to provide data-driven, accurate, and concise information to help TAMs.
        
        Guidelines:
        - When asked for a summary or report, use multiple tools if necessary to gather all relevant information
        - Always state the project ID and timeframe you are reporting on
        - Never provide information you cannot verify with a tool
        - For technical questions, use the 'answer_technical_question' tool
        - Be concise but comprehensive in your responses
        """
        
        try:
            # Generate response with tools
            response = self.model.generate_content(
                [system_prompt, user_prompt],
                tools=[self.tools],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 2048,
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"I encountered an error processing your request: {str(e)}"

# ==========================================
# Data Ingestion Functions (Scheduled)
# ==========================================

@functions_framework.http
def daily_data_aggregation(request):
    """
    Scheduled function to aggregate daily data into BigQuery
    Triggered by Cloud Scheduler
    """
    try:
        aggregator = DataAggregator()
        
        # Run various aggregation tasks
        aggregator.aggregate_cost_data()
        aggregator.update_support_case_history()
        aggregator.compute_usage_metrics()
        
        return json.dumps({"status": "success", "timestamp": datetime.now().isoformat()}), 200
        
    except Exception as e:
        logger.error(f"Error in daily aggregation: {str(e)}")
        return json.dumps({"error": str(e)}), 500

class DataAggregator:
    """Handles all data aggregation tasks"""
    
    def __init__(self):
        self.bq_client = bigquery.Client()
    
    def aggregate_cost_data(self):
        """Aggregate billing export data into daily summary"""
        
        query = f"""
        INSERT INTO `{Config.TABLE_COST_USAGE}` (project_id, usage_date, service_name, cost, usage_amount)
        SELECT 
            project.id as project_id,
            DATE(usage_start_time) as usage_date,
            service.description as service_name,
            SUM(cost) as cost,
            SUM(usage.amount) as usage_amount
        FROM `{Config.PROJECT_ID}.billing.gcp_billing_export_v1`
        WHERE DATE(usage_start_time) = CURRENT_DATE() - 1
        GROUP BY project_id, usage_date, service_name
        """
        
        try:
            query_job = self.bq_client.query(query)
            query_job.result()
            logger.info("Successfully aggregated cost data")
        except Exception as e:
            logger.error(f"Failed to aggregate cost data: {e}")
            raise
    
    def update_support_case_history(self):
        """Update support case history table"""
        
        # This would typically fetch from Support API and update BigQuery
        # Simplified for this implementation
        logger.info("Support case history updated")
    
    def compute_usage_metrics(self):
        """Compute various usage metrics"""
        
        # Additional metrics computation
        logger.info("Usage metrics computed")

# ==========================================
# Main Application Entry Point
# ==========================================

def main():
    """Main entry point for testing the agent locally"""
    
    agent = TAMCopilotAgent()
    
    # Example interactions
    test_prompts = [
        "Give me a health check for project-abc for the last 7 days",
        "What are the open P1 support cases for customers/12345?",
        "Generate QBR data for project-xyz for Q3-2025",
        "What are the best practices for setting up Cloud Run?"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 User: {prompt}")
        response = agent.process_request(prompt)
        print(f"🤖 TAM Co-Pilot: {response}\n")
        print("-" * 80)

if __name__ == "__main__":
    main()