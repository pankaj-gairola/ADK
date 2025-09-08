from adk.api.tools import tool

@tool
def gcp_monitoring_tool(customer_project_id: str) -> str:
    """
    Analyzes Google Cloud Monitoring data for a specific customer project.
    Identifies services with high latency, error rates, or saturation.
    In a real implementation, this would call the Cloud Monitoring API.
    """
    print(f"TOOL: Analyzing monitoring data for project '{customer_project_id}'...")
    # Mock implementation
    return (
        "Analysis Complete:\n"
        "- The 'billing-service' is showing a 20% increase in p99 latency week-over-week.\n"
        "- The 'frontend-load-balancer' has a 5% error rate, which is above the 1% SLO.\n"
        "- All other services are within normal operating parameters."
    )

@tool
def gcp_billing_tool(customer_project_id: str) -> str:
    """
    Analyzes Google Cloud Billing data for cost-saving opportunities.
    In a real implementation, this would call the Cloud Billing API.
    """
    print(f"TOOL: Analyzing billing data for project '{customer_project_id}'...")
    # Mock implementation
    return (
        "Analysis Complete:\n"
        "- Identified 5 large, idle n2-standard-16 VMs that could be shut down, saving an estimated $2,100/month.\n"
        "- Recommends applying a Committed Use Discount for GKE resources, saving an estimated $4,500/month."
    )

@tool
def gcp_usage_tool(customer_project_id: str) -> str:
    """
    Gathers detailed service usage statistics for a customer project.
    Used for QBR preparation.
    In a real implementation, this would query billing export data or usage APIs.
    """
    print(f"TOOL: Gathering quarterly usage data for project '{customer_project_id}'...")
    # Mock implementation
    return (
        "Quarterly Usage Data:\n"
        "- GCE Core-hours: 1.2M (up 15% from last quarter)\n"
        "- GKE Pod-hours: 3.5M (up 30% from last quarter)\n"
        "- BigQuery Bytes Scanned: 500TB (up 25% from last quarter)\n"
        "- New Services Adopted: Cloud Run, AlloyDB."
    )
