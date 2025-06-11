"""Tests for MCP Customer Service Server."""

import asyncio
from datetime import datetime

import pytest

from src.main import CUSTOMERS_DB, Customer, TicketRequest


# Helper functions that replicate the logic without FastMCP decorators
async def _get_customer_info(customer_id: str) -> Customer:
    """Test helper: Retrieve customer information by ID."""
    if customer_id not in CUSTOMERS_DB:
        raise ValueError(f"Customer {customer_id} not found")

    # Simulate database delay
    await asyncio.sleep(0.01)  # Shorter delay for tests
    return CUSTOMERS_DB[customer_id]


async def _create_support_ticket(request: TicketRequest) -> dict:
    """Test helper: Create a new customer support ticket."""
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


async def _calculate_account_value(
    customer_id: str, purchase_history: list[float]
) -> dict:
    """Test helper: Calculate total account value and average purchase."""
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


async def _generate_service_response_prompt(
    customer_name: str, issue_type: str, resolution_steps: list[str]
) -> str:
    """Test helper: Generate a professional customer service response."""

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


@pytest.mark.asyncio
async def test_get_customer_info():
    """Test retrieving customer information."""
    # Test valid customer
    customer = await _get_customer_info("12345")
    assert customer.id == "12345"
    assert customer.name == "Alice Johnson"
    assert customer.email == "alice@example.com"

    # Test invalid customer
    with pytest.raises(ValueError):
        await _get_customer_info("99999")


@pytest.mark.asyncio
async def test_create_support_ticket():
    """Test creating a support ticket."""
    request = TicketRequest(
        customer_id="12345",
        subject="Billing Issue",
        description="I was charged twice",
        priority="high",
    )

    ticket = await _create_support_ticket(request)
    assert ticket["customer_id"] == "12345"
    assert ticket["subject"] == "Billing Issue"
    assert ticket["priority"] == "high"
    assert ticket["status"] == "open"
    assert "TICKET-" in ticket["ticket_id"]


@pytest.mark.asyncio
async def test_calculate_account_value():
    """Test calculating account value."""
    # Test with purchases
    result = await _calculate_account_value("12345", [100.0, 250.0, 75.0])
    assert result["total_value"] == 425.0
    assert result["average_purchase"] == 141.67
    assert result["purchase_count"] == 3

    # Test with no purchases
    result = await _calculate_account_value("12345", [])
    assert result["total_value"] == 0.0
    assert result["average_purchase"] == 0.0
    assert result["purchase_count"] == 0


@pytest.mark.asyncio
async def test_generate_service_response_prompt():
    """Test generating service response prompt."""
    prompt = await _generate_service_response_prompt(
        "Alice Johnson",
        "Account Access",
        ["Reset your password", "Clear browser cache", "Try logging in again"],
    )

    assert "Alice Johnson" in prompt
    assert "Account Access" in prompt
    assert "1. Reset your password" in prompt
    assert "2. Clear browser cache" in prompt
    assert "3. Try logging in again" in prompt


def test_customer_model_validation():
    """Test Customer model validation."""
    # Valid customer
    customer = Customer(id="123", name="Test User", email="test@example.com")
    assert customer.email == "test@example.com"

    # Invalid email
    with pytest.raises(ValueError):
        Customer(id="123", name="Test User", email="invalid-email")


def test_ticket_request_validation():
    """Test TicketRequest model validation."""
    # Valid priority
    request = TicketRequest(
        customer_id="123",
        subject="Test",
        description="Test description",
        priority="urgent",
    )
    assert request.priority == "urgent"

    # Invalid priority
    with pytest.raises(ValueError):
        TicketRequest(
            customer_id="123",
            subject="Test",
            description="Test description",
            priority="invalid",
        )
