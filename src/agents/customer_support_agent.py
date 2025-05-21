"""
Customer Support Agent with custom tools for the Agent Swarm system.

This agent is responsible for handling customer support queries and providing
assistance with account-related issues.
"""
from typing import Dict, Any, List, Optional
import os
import json
import random
from datetime import datetime, timedelta

from .base_agent import BaseAgent


class AccountStatusTool:
    """Tool for checking account status and recent transactions."""
    
    def __init__(self):
        """Initialize the account status tool."""
        # In a real implementation, this would connect to a database or API
        # For this demo, we'll use simulated data
        self.user_data = {
            # Simulated user data store
        }
    
    def get_account_status(self, user_id: str) -> Dict[str, Any]:
        """Get the account status for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dict containing account status information
        """
        # Simulate fetching account data
        # In a real implementation, this would query a database or API
        
        # Generate random account data if we don't have it for this user
        if user_id not in self.user_data:
            self.user_data[user_id] = self._generate_mock_account_data(user_id)
            
        return self.user_data[user_id]
    
    def get_recent_transactions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent transactions for a user.
        
        Args:
            user_id: The ID of the user
            days: Number of days to look back
            
        Returns:
            List of recent transactions
        """
        # Ensure we have data for this user
        if user_id not in self.user_data:
            self.user_data[user_id] = self._generate_mock_account_data(user_id)
            
        # Get transactions from the last N days
        account_data = self.user_data[user_id]
        transactions = account_data.get("transactions", [])
        
        # Filter to only include recent transactions
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_transactions = [
            t for t in transactions 
            if datetime.fromisoformat(t["date"]) > cutoff_date
        ]
        
        return recent_transactions
    
    def _generate_mock_account_data(self, user_id: str) -> Dict[str, Any]:
        """Generate mock account data for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dict containing mock account data
        """
        # Account statuses
        statuses = ["active", "restricted", "pending_verification", "locked"]
        status_weights = [0.7, 0.1, 0.1, 0.1]  # Most accounts are active
        
        # Generate a random account status
        account_status = random.choices(statuses, status_weights)[0]
        
        # Generate random balance
        balance = round(random.uniform(100, 5000), 2)
        
        # Generate random transactions
        num_transactions = random.randint(5, 15)
        transactions = []
        
        for _ in range(num_transactions):
            # Random date in the last 30 days
            days_ago = random.randint(0, 30)
            transaction_date = datetime.now() - timedelta(days=days_ago)
            
            # Random amount (negative for debits, positive for credits)
            amount = round(random.uniform(-500, 500), 2)
            
            # Transaction types
            if amount < 0:
                transaction_type = random.choice(["purchase", "transfer_out", "withdrawal", "payment"])
            else:
                transaction_type = random.choice(["deposit", "transfer_in", "refund", "payment_received"])
                
            # Create transaction
            transaction = {
                "id": f"txn_{random.randint(10000, 99999)}",
                "date": transaction_date.isoformat(),
                "amount": amount,
                "type": transaction_type,
                "description": f"{transaction_type.replace('_', ' ').title()} - {abs(amount):.2f} BRL",
                "status": random.choice(["completed", "pending", "failed"]),
            }
            
            transactions.append(transaction)
            
        # Sort transactions by date (newest first)
        transactions.sort(key=lambda x: x["date"], reverse=True)
        
        # Create account data
        account_data = {
            "user_id": user_id,
            "account_number": f"ACCT-{random.randint(10000, 99999)}",
            "status": account_status,
            "balance": balance,
            "currency": "BRL",
            "last_login": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            "transactions": transactions
        }
        
        return account_data


class TroubleshootingTool:
    """Tool for troubleshooting common account issues."""
    
    def __init__(self):
        """Initialize the troubleshooting tool."""
        # Common issues and their solutions
        self.troubleshooting_guides = {
            "login_issues": {
                "title": "Login Issues",
                "symptoms": ["can't sign in", "unable to log in", "login not working", "password not accepted"],
                "solutions": [
                    "Reset your password through the 'Forgot Password' link on the login page",
                    "Ensure you're using the correct email address associated with your account",
                    "Check if Caps Lock is enabled when typing your password",
                    "Clear your browser cache and cookies, then try again",
                    "Try using a different browser or device",
                    "Ensure your account hasn't been locked due to multiple failed login attempts"
                ],
                "escalation": "If you've tried these steps and still can't log in, please contact our support team with your account email for further assistance."
            },
            "transfer_issues": {
                "title": "Transfer Issues",
                "symptoms": ["can't make transfers", "transfer failed", "payment not going through", "transaction error"],
                "solutions": [
                    "Check your account balance to ensure you have sufficient funds",
                    "Verify that your account status is active and not restricted",
                    "Ensure you're entering the correct recipient information",
                    "Check if you've reached your daily or monthly transfer limits",
                    "Try making a smaller transfer to see if the issue is amount-related",
                    "Ensure your internet connection is stable when making the transfer"
                ],
                "escalation": "If transfers are still failing after these steps, please contact our support team with the specific error message or transaction ID for assistance."
            },
            "app_issues": {
                "title": "Mobile App Issues",
                "symptoms": ["app crashing", "app not loading", "features not working", "app error"],
                "solutions": [
                    "Update to the latest version of the app from your device's app store",
                    "Restart your device and try opening the app again",
                    "Check your internet connection and ensure it's stable",
                    "Clear the app cache in your device settings",
                    "Uninstall and reinstall the app",
                    "Ensure your device meets the minimum requirements for the app"
                ],
                "escalation": "If you're still experiencing issues with the app, please contact our support team with your device model and operating system version for further assistance."
            },
            "card_issues": {
                "title": "Card Issues",
                "symptoms": ["card declined", "card not working", "payment failed", "card blocked"],
                "solutions": [
                    "Check your card balance to ensure you have sufficient funds",
                    "Verify that your card is activated and not expired",
                    "Ensure you're entering the correct card details for online purchases",
                    "Check if international transactions are enabled for your card",
                    "Temporarily lock and unlock your card through the app",
                    "Check if the merchant accepts your card type"
                ],
                "escalation": "If your card is still not working after these steps, please contact our support team for immediate assistance."
            }
        }
    
    def identify_issue(self, message: str) -> Dict[str, Any]:
        """Identify the issue based on the user's message.
        
        Args:
            message: The user's message describing their issue
            
        Returns:
            Dict containing the identified issue and troubleshooting information
        """
        message_lower = message.lower()
        
        # Check each issue category for matching symptoms
        for issue_key, issue_data in self.troubleshooting_guides.items():
            for symptom in issue_data["symptoms"]:
                if symptom in message_lower:
                    return {
                        "issue_type": issue_key,
                        "title": issue_data["title"],
                        "solutions": issue_data["solutions"],
                        "escalation": issue_data["escalation"]
                    }
        
        # If no specific issue is identified, return a general response
        return {
            "issue_type": "general",
            "title": "General Issue",
            "solutions": [
                "Please provide more details about the specific issue you're experiencing",
                "Check our help center for guides on common issues",
                "Ensure your app and device are updated to the latest versions",
                "Try restarting your device and the app"
            ],
            "escalation": "If you need immediate assistance, please contact our support team with details of your issue."
        }


class CustomerSupportAgent(BaseAgent):
    """
    Customer Support Agent that handles support queries and account issues.
    
    This agent uses custom tools to retrieve account information and provide
    troubleshooting assistance.
    """
    
    def __init__(self, name: str = "Customer Support"):
        """Initialize the Customer Support Agent.
        
        Args:
            name: The name of the agent
        """
        super().__init__(name)
        self.account_tool = AccountStatusTool()
        self.troubleshooting_tool = TroubleshootingTool()
    
    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a support message and provide assistance.
        
        Args:
            message: The user message to process
            user_id: The ID of the user sending the message
            context: Optional context information
            
        Returns:
            Dict containing the response and any additional information
        """
        # First, check if this is a troubleshooting issue
        troubleshooting_result = self.troubleshooting_tool.identify_issue(message)
        self.record_tool_call("troubleshooting", troubleshooting_result)
        
        # Get account status information
        account_status = self.account_tool.get_account_status(user_id)
        self.record_tool_call("account_status", {"user_id": user_id, "status": account_status["status"]})
        
        # Get recent transactions if relevant to the issue
        if troubleshooting_result["issue_type"] in ["transfer_issues", "card_issues"]:
            recent_transactions = self.account_tool.get_recent_transactions(user_id, days=7)
            self.record_tool_call("recent_transactions", {"user_id": user_id, "count": len(recent_transactions)})
        
        # Generate a response based on the issue and account information
        response = self._generate_support_response(message, troubleshooting_result, account_status)
        
        return {
            "response": response,
            "agent_type": "support"
        }
    
    def _generate_support_response(self, message: str, troubleshooting: Dict[str, Any], account: Dict[str, Any]) -> str:
        """Generate a support response based on the issue and account information.
        
        Args:
            message: The original user message
            troubleshooting: Troubleshooting information
            account: Account status information
            
        Returns:
            Support response string
        """
        # Start with a greeting
        response = f"I understand you're having an issue with {troubleshooting['title'].lower()}. "
        
        # Add account status context
        if account["status"] != "active":
            response += f"I noticed that your account status is currently '{account['status']}', which might be related to your issue. "
        
        # Add troubleshooting steps
        response += "Here are some steps that might help:\n\n"
        for i, solution in enumerate(troubleshooting["solutions"], 1):
            response += f"{i}. {solution}\n"
        
        # Add account-specific advice
        if troubleshooting["issue_type"] == "login_issues" and account["status"] == "locked":
            response += "\nYour account appears to be locked. This is often due to multiple failed login attempts. "
            response += "You'll need to contact our support team to unlock your account.\n"
        
        elif troubleshooting["issue_type"] == "transfer_issues":
            if account["balance"] < 10:
                response += f"\nI noticed your account balance is low (R${account['balance']:.2f}), which might be preventing transfers.\n"
            elif account["status"] == "restricted":
                response += "\nYour account currently has restrictions that may be limiting transfer capabilities.\n"
        
        # Add escalation information
        response += f"\n{troubleshooting['escalation']}"
        
        return response
