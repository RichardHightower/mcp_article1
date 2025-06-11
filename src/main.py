import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Customer Service Assistant")


# Data models for type safety and validation
class Customer(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    account_status: str = "active"
    last_interaction: Optional[datetime] = None

    @field_validator("email", mode='after') # noqa
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v:
            raise PydanticCustomError(
                'invalid_email',
                'Invalid email format: {email} must contain @',
                {'email': v},
            )
        return v


class TicketRequest(BaseModel):
    customer_id: str
    subject: str
    description: str
    priority: str = "normal"

    @field_validator("priority", mode='after') # noqa
    @classmethod
    def priority_must_be_valid(cls, v: str) -> str:
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise PydanticCustomError(
                'invalid_priority',
                'Priority must be one of: {valid_priorities}, got {priority}',
                {'valid_priorities': ', '.join(valid_priorities), 'priority': v},
            )
        return v


# Simulated customer database
CUSTOMERS_DB = {
    "12345": Customer(
        id="12345",
        name="Alice Johnson",
        email="alice@example.com",
        phone="+1-555-0123",
        account_status="active",
        last_interaction=datetime.now(),
    ),
    "67890": Customer(
        id="67890",
        name="Bob Smith",
        email="bob@example.com",
        account_status="suspended",
    ),
}


# MCP Resource: Customer Data Access
@mcp.resource("customer://{customer_id}")
async def get_customer_info(customer_id: str) -> Customer:
    """Retrieve customer information by ID."""
    logger.info(f"Retrieving customer info for ID: {customer_id}")

    if customer_id not in CUSTOMERS_DB:
        raise ValueError(f"Customer {customer_id} not found")

    # Simulate database delay
    await asyncio.sleep(0.1)
    return CUSTOMERS_DB[customer_id]


@mcp.tool()
async def get_recent_customers(limit: int = 10) -> List[Customer]:
    """Retrieve recently active customers."""
    logger.info(f"Retrieving {limit} recent customers")

    # Sort by last interaction, return most recent
    sorted_customers = sorted(
        CUSTOMERS_DB.values(),
        key=lambda c: c.last_interaction or datetime.min,
        reverse=True,
    )

    return sorted_customers[:limit]


# MCP Tool: Create Support Ticket
@mcp.tool()
async def create_support_ticket(request: TicketRequest) -> dict:
    """Create a new customer support ticket."""
    logger.info(f"Creating ticket for customer {request.customer_id}")

    # Validate customer exists
    if request.customer_id not in CUSTOMERS_DB:
        raise ValueError(f"Customer {request.customer_id} not found")

    # Simulate ticket creation
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": request.customer_id,
        "subject": request.subject,
        "description": request.description,
        "priority": request.priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
    }

    return ticket


# MCP Tool: Calculate Account Value
@mcp.tool()
async def calculate_account_value(
    customer_id: str, purchase_history: List[float]
) -> dict:
    """Calculate total account value and average purchase."""
    logger.info(f"Calculating account value for {customer_id}")

    if not purchase_history:
        return {
            "customer_id": customer_id,
            "total_value": 0.0,
            "average_purchase": 0.0,
            "purchase_count": 0,
        }

    total = sum(purchase_history)
    average = total / len(purchase_history)

    return {
        "customer_id": customer_id,
        "total_value": round(total, 2),
        "average_purchase": round(average, 2),
        "purchase_count": len(purchase_history),
    }


# MCP Prompt: Customer Service Response Template
@mcp.prompt("customer_service_response")
async def generate_service_response_prompt(
    customer_name: str, issue_type: str, resolution_steps: List[str]
) -> str:
    """Generate a professional customer service response."""

    steps_text = "\n".join(
        [f"{i+1}. {step}" for i, step in enumerate(resolution_steps)]
    )

    return f"""
You are a professional customer service representative.
Generate a helpful and empathetic response for the customer.

Customer: {customer_name}
Issue Type: {issue_type}

Resolution Steps:
{steps_text}

Guidelines:
- Be professional but warm
- Acknowledge the customer's concern
- Provide clear, actionable steps
- End with an offer for further assistance
- Keep the tone positive and solution-focused

Generate a complete customer service response
following these guidelines.
"""


def main():
    """Main entry point for the MCP server."""
    print("🚀 Starting Customer Service MCP Server...")
    print("📋 Available Resources:")
    print("   - customer://{customer_id} - Get customer info")
    print("🔧 Available Tools:")
    print("   - get_recent_customers - Get recent customers")
    print("   - create_support_ticket - Create support ticket")
    print("   - calculate_account_value - Calculate account value")
    print("📝 Available Prompts:")
    print("   - customer_service_response - Generate responses")
    print("\n✅ Server ready for connections!")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
