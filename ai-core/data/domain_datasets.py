"""Multi-organization domain instruction datasets for federated learning simulation."""
import random
import logging
from typing import Dict, List
from torch.utils.data import DataLoader
from .text_dataset import QwenTextDataset, create_text_data_loader

logger = logging.getLogger(__name__)

# Sample multi-domain org datasets (Tech Support, Healthcare, E-Commerce, Code/DB)
ORG_DOMAINS: Dict[str, Dict[str, any]] = {
    "org_tech_support": {
        "name": "CloudOps Tech Support",
        "description": "Server diagnostics, system status checks, process restarts",
        "data": [
            {
                "prompt": "Server web-01 is returning HTTP 500 errors. Can you check its status?",
                "response": "I will check the status of server `web-01`.\n<tool_call>{\"name\": \"get_server_status\", \"arguments\": {\"server_id\": \"web-01\"}}</tool_call>"
            },
            {
                "prompt": "Restart the caching daemon redis-cache-2 immediately.",
                "response": "Executing restart command for service `redis-cache-2`.\n<tool_call>{\"name\": \"restart_service\", \"arguments\": {\"service_name\": \"redis-cache-2\"}}</tool_call>"
            },
            {
                "prompt": "What is the CPU usage on db-master-01?",
                "response": "Let me query system metrics for `db-master-01`.\n<tool_call>{\"name\": \"get_server_status\", \"arguments\": {\"server_id\": \"db-master-01\"}}</tool_call>"
            },
            {
                "prompt": "How do I check system disk space?",
                "response": "Use the command `df -h` or run the system status diagnostic tool to inspect available storage on all mounted partitions."
            },
            {
                "prompt": "Clear the temporary log directory for app-worker-04.",
                "response": "Clearing temporary logs on `app-worker-04`.\n<tool_call>{\"name\": \"clear_logs\", \"arguments\": {\"server_id\": \"app-worker-04\", \"log_type\": \"temp\"}}</tool_call>"
            },
        ]
    },
    "org_healthcare": {
        "name": "HealthShield Medical Triage",
        "description": "Patient record lookup, lab results query, medication safety",
        "data": [
            {
                "prompt": "Lookup lab results for patient ID P-84920.",
                "response": "Retrieving lab results for patient P-84920.\n<tool_call>{\"name\": \"get_lab_results\", \"arguments\": {\"patient_id\": \"P-84920\"}}</tool_call>"
            },
            {
                "prompt": "Check interaction between Amoxicillin and Warfarin for patient P-10293.",
                "response": "Checking drug interaction database for Amoxicillin and Warfarin.\n<tool_call>{\"name\": \"check_drug_interaction\", \"arguments\": {\"drug1\": \"Amoxicillin\", \"drug2\": \"Warfarin\"}}</tool_call>"
            },
            {
                "prompt": "Schedule a follow-up appointment for patient P-33120 with Dr. Smith.",
                "response": "Scheduling appointment for patient P-33120.\n<tool_call>{\"name\": \"schedule_appointment\", \"arguments\": {\"patient_id\": \"P-33120\", \"doctor\": \"Dr. Smith\"}}</tool_call>"
            },
            {
                "prompt": "What are common side effects of Lisinopril?",
                "response": "Common side effects of Lisinopril include dry cough, dizziness, headache, and elevated potassium levels. Consult a physician if severe."
            },
            {
                "prompt": "Verify patient P-94021 emergency contact details.",
                "response": "Retrieving emergency contacts for P-94021.\n<tool_call>{\"name\": \"get_patient_records\", \"arguments\": {\"patient_id\": \"P-94021\"}}</tool_call>"
            },
        ]
    },
    "org_ecommerce": {
        "name": "ShopVault Customer Service",
        "description": "Order tracking, refund processing, inventory stock checks",
        "data": [
            {
                "prompt": "Where is order ORD-99381? The customer says it hasn't arrived.",
                "response": "Fetching real-time tracking info for order ORD-99381.\n<tool_call>{\"name\": \"track_order\", \"arguments\": {\"order_id\": \"ORD-99381\"}}</tool_call>"
            },
            {
                "prompt": "Issue a full refund for returned item in order ORD-44102.",
                "response": "Initiating refund process for order ORD-44102.\n<tool_call>{\"name\": \"process_refund\", \"arguments\": {\"order_id\": \"ORD-44102\", \"type\": \"full\"}}</tool_call>"
            },
            {
                "prompt": "Do we have stock for SKU-WIRELESS-EARBUDS in warehouse WH-2?",
                "response": "Checking inventory levels for SKU-WIRELESS-EARBUDS in warehouse WH-2.\n<tool_call>{\"name\": \"check_inventory\", \"arguments\": {\"sku\": \"SKU-WIRELESS-EARBUDS\", \"warehouse\": \"WH-2\"}}</tool_call>"
            },
            {
                "prompt": "What is our store return policy?",
                "response": "Customers can return items within 30 days of purchase in original packaging for a full refund or store credit."
            },
            {
                "prompt": "Update delivery address for ORD-88120 to '123 Main St'.",
                "response": "Updating shipping address for order ORD-88120.\n<tool_call>{\"name\": \"update_order_address\", \"arguments\": {\"order_id\": \"ORD-88120\", \"new_address\": \"123 Main St\"}}</tool_call>"
            },
        ]
    },
    "org_code_dev": {
        "name": "DevPulse Software Engineering",
        "description": "SQL queries, repository commits check, automated test execution",
        "data": [
            {
                "prompt": "Query active user count from the `users` table created in the last 7 days.",
                "response": "Executing SQL query on database.\n<tool_call>{\"name\": \"execute_sql\", \"arguments\": {\"query\": \"SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL 7 DAY;\"}}</tool_call>"
            },
            {
                "prompt": "Run unit test suite for module auth_service.",
                "response": "Running unit tests for `auth_service`.\n<tool_call>{\"name\": \"run_test_suite\", \"arguments\": {\"module_name\": \"auth_service\"}}</tool_call>"
            },
            {
                "prompt": "Check the last 3 git commits on branch main.",
                "response": "Fetching git commit log for branch main.\n<tool_call>{\"name\": \"get_git_log\", \"arguments\": {\"branch\": \"main\", \"count\": 3}}</tool_call>"
            },
            {
                "prompt": "What is the difference between inner join and left join in SQL?",
                "response": "INNER JOIN returns rows with matching values in both tables. LEFT JOIN returns all rows from the left table and matched rows from the right table."
            },
            {
                "prompt": "Execute benchmark test on database pool connection.",
                "response": "Running connection pool benchmark.\n<tool_call>{\"name\": \"run_test_suite\", \"arguments\": {\"module_name\": \"db_pool_benchmark\"}}</tool_call>"
            },
        ]
    }
}


def get_org_dataset(
    org_key: str,
    tokenizer,
    max_length: int = 256,
    multiplier: int = 10,
) -> QwenTextDataset:
    """
    Get tokenized dataset for a specific simulated organization.
    Multiplies base sample examples to simulate larger dataset sizes.
    """
    if org_key not in ORG_DOMAINS:
        raise ValueError(f"Unknown org_key '{org_key}'. Options: {list(ORG_DOMAINS.keys())}")

    base_data = ORG_DOMAINS[org_key]["data"]
    expanded_data = base_data * multiplier
    random.seed(42)
    random.shuffle(expanded_data)

    return QwenTextDataset(expanded_data, tokenizer, max_length=max_length)


def get_all_org_data_loaders(
    tokenizer,
    batch_size: int = 2,
    max_length: int = 256,
) -> Dict[str, Dict[str, DataLoader]]:
    """
    Generate train and test DataLoaders for all 4 simulated organizations.
    """
    org_loaders = {}
    for org_key in ORG_DOMAINS:
        full_dataset = get_org_dataset(org_key, tokenizer, max_length=max_length, multiplier=8)
        split_idx = int(len(full_dataset) * 0.8)
        
        train_data = full_dataset.examples[:split_idx]
        test_data = full_dataset.examples[split_idx:]

        class SubsetTextDataset:
            def __init__(self, examples):
                self.examples = examples
            def __len__(self):
                return len(self.examples)
            def __getitem__(self, idx):
                return self.examples[idx]

        train_loader = DataLoader(SubsetTextDataset(train_data), batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(SubsetTextDataset(test_data), batch_size=batch_size, shuffle=False)

        org_loaders[org_key] = {
            "train": train_loader,
            "test": test_loader,
            "info": ORG_DOMAINS[org_key],
        }
    return org_loaders
