"""
Unit tests for the Customer Support Agent.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.customer_support_agent import CustomerSupportAgent, AccountStatusTool, TroubleshootingTool


@pytest.fixture
def mock_account_tool():
    """Create a mock account status tool."""
    mock = MagicMock(spec=AccountStatusTool)
    mock.get_account_status.return_value = {
        "user_id": "test_user",
        "account_number": "ACCT-12345",
        "status": "active",
        "balance": 1000.0,
        "currency": "BRL",
        "last_login": "2025-05-20T10:00:00",
        "transactions": []
    }
    mock.get_recent_transactions.return_value = [
        {
            "id": "txn_12345",
            "date": "2025-05-20T10:00:00",
            "amount": -50.0,
            "type": "purchase",
            "description": "Purchase - 50.00 BRL",
            "status": "completed"
        }
    ]
    return mock


@pytest.fixture
def mock_troubleshooting_tool():
    """Create a mock troubleshooting tool."""
    mock = MagicMock(spec=TroubleshootingTool)
    mock.identify_issue.return_value = {
        "issue_type": "login_issues",
        "title": "Login Issues",
        "solutions": ["Reset your password", "Check your email"],
        "escalation": "Contact support if issues persist"
    }
    return mock


@pytest.mark.asyncio
async def test_customer_support_agent_initialization():
    """Test that the customer support agent initializes correctly."""
    agent = CustomerSupportAgent()
    assert agent.name == "Customer Support"
    assert isinstance(agent.account_tool, AccountStatusTool)
    assert isinstance(agent.troubleshooting_tool, TroubleshootingTool)


@pytest.mark.asyncio
async def test_customer_support_agent_process(mock_account_tool, mock_troubleshooting_tool):
    """Test that the customer support agent processes queries correctly."""
    # Create agent with mock tools
    agent = CustomerSupportAgent()
    agent.account_tool = mock_account_tool
    agent.troubleshooting_tool = mock_troubleshooting_tool
    
    # Process a query
    result = await agent.process("I can't log in to my account", "user123")
    
    # Verify the agent processed the query correctly
    mock_troubleshooting_tool.identify_issue.assert_called_once()
    mock_account_tool.get_account_status.assert_called_once()
    assert "response" in result
    assert "agent_type" in result
    assert result["agent_type"] == "support"


def test_account_status_tool():
    """Test the account status tool functionality."""
    tool = AccountStatusTool()
    
    # Test getting account status
    status = tool.get_account_status("test_user")
    assert "user_id" in status
    assert "account_number" in status
    assert "status" in status
    assert "balance" in status
    assert "transactions" in status
    
    # Test getting recent transactions
    transactions = tool.get_recent_transactions("test_user", days=7)
    assert isinstance(transactions, list)
    
    # Test that the same user gets consistent data
    status2 = tool.get_account_status("test_user")
    assert status["account_number"] == status2["account_number"]


def test_troubleshooting_tool():
    """Test the troubleshooting tool functionality."""
    tool = TroubleshootingTool()
    
    # Test login issues
    login_result = tool.identify_issue("I can't sign in to my account")
    assert login_result["issue_type"] == "login_issues"
    assert "solutions" in login_result
    assert "escalation" in login_result
    
    # Test transfer issues
    transfer_result = tool.identify_issue("I can't make transfers from my account")
    assert transfer_result["issue_type"] == "transfer_issues"
    
    # Test general issues
    general_result = tool.identify_issue("I have a question about something")
    assert general_result["issue_type"] == "general"


@pytest.mark.asyncio
async def test_generate_support_response():
    """Test the support response generation."""
    agent = CustomerSupportAgent()
    
    # Test response generation
    troubleshooting = {
        "issue_type": "login_issues",
        "title": "Login Issues",
        "solutions": ["Reset your password", "Check your email"],
        "escalation": "Contact support if issues persist"
    }
    
    account = {
        "user_id": "test_user",
        "account_number": "ACCT-12345",
        "status": "locked",
        "balance": 1000.0,
        "currency": "BRL",
        "last_login": "2025-05-20T10:00:00",
        "transactions": []
    }
    
    response = agent._generate_support_response(
        "I can't log in", troubleshooting, account
    )
    
    # Verify the response contains key elements
    assert "login issues" in response.lower()
    assert "locked" in response
    assert "Reset your password" in response
    assert "Contact support" in response
