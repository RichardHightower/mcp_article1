"""Tests for MCP Customer Service Server."""


import pytest

from src.main import (Customer, TicketRequest, calculate_account_value,
                      create_support_ticket, generate_service_response_prompt,
                      get_customer_info)


@pytest.mark.asyncio
async def test_get_customer_info():
    """Test retrieving customer information."""
    # Test valid customer
    customer = await get_customer_info("12345")
    assert customer.id == "12345"
    assert customer.name == "Alice Johnson"
    assert customer.email == "alice@example.com"

    # Test invalid customer
    with pytest.raises(ValueError):
        await get_customer_info("99999")


@pytest.mark.asyncio
async def test_create_support_ticket():
    """Test creating a support ticket."""
    request = TicketRequest(
        customer_id="12345",
        subject="Billing Issue",
        description="I was charged twice",
        priority="high",
    )

    ticket = await create_support_ticket(request)
    assert ticket["customer_id"] == "12345"
    assert ticket["subject"] == "Billing Issue"
    assert ticket["priority"] == "high"
    assert ticket["status"] == "open"
    assert "TICKET-" in ticket["ticket_id"]


@pytest.mark.asyncio
async def test_calculate_account_value():
    """Test calculating account value."""
    # Test with purchases
    result = await calculate_account_value("12345", [100.0, 250.0, 75.0])
    assert result["total_value"] == 425.0
    assert result["average_purchase"] == 141.67
    assert result["purchase_count"] == 3

    # Test with no purchases
    result = await calculate_account_value("12345", [])
    assert result["total_value"] == 0.0
    assert result["average_purchase"] == 0.0
    assert result["purchase_count"] == 0


@pytest.mark.asyncio
async def test_generate_service_response_prompt():
    """Test generating service response prompt."""
    prompt = await generate_service_response_prompt(
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
