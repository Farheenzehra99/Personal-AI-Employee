#!/usr/bin/env python3
"""
Odoo Accounting Integration - MCP Server Wrapper for AI Employee
Connects to Odoo Community Edition for accounting automation
"""

import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Try to import xmlrpc for Odoo API
try:
    import xmlrpc.client
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    logging.warning("xmlrpc not installed. Install with: pip install xmlrpc")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OdooIntegration')


class OdooAccounting:
    """Odoo Accounting Integration"""
    
    def __init__(self, config_path: str = None):
        """Initialize Odoo connection"""
        # Config is now in parent directory (project root) or odoo folder
        default_config = Path(__file__).parent.parent / 'odoo_config.json'
        if not default_config.exists():
            default_config = Path(__file__).parent / 'odoo_config.json'
        self.config_path = config_path or default_config
        self.config = self._load_config()
        self.uid = None
        self.common = None
        self.models = None
        
        if ODOO_AVAILABLE:
            self._connect()

    def _load_config(self) -> Dict:
        """Load Odoo configuration"""
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text())
            logger.info(f"Loaded Odoo config from {self.config_path}")
            return config
        
        # Default config
        logger.warning("Odoo config not found, using defaults")
        return {
            'url': 'http://localhost:8069',
            'db': 'ai_employee',
            'username': 'admin@example.com',
            'password': 'admin',
        }

    def _connect(self):
        """Connect to Odoo"""
        try:
            # Common endpoint
            self.common = xmlrpc.client.ServerProxy(f'{self.config["url"]}/xmlrpc/2/common')
            
            # Authenticate
            self.uid = self.common.authenticate(
                self.config['db'],
                self.config['username'],
                self.config['password'],
                {}
            )
            
            if not self.uid:
                logger.error("Odoo authentication failed")
                return
            
            # Models endpoint
            self.models = xmlrpc.client.ServerProxy(f'{self.config["url"]}/xmlrpc/2/object')
            
            logger.info(f"Connected to Odoo: {self.config['url']} (User ID: {self.uid})")
            
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")

    def get_invoices(self, limit: int = 50, state: str = None) -> List[Dict]:
        """Get invoices from Odoo"""
        if not self.models:
            return []
        
        try:
            domain = []
            if state:
                domain.append(('state', '=', state))
            
            invoice_ids = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.move',
                'search',
                [domain],
                {'limit': limit, 'order': 'invoice_date DESC'}
            )
            
            invoices = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.move',
                'read',
                [invoice_ids],
                {'fields': ['name', 'partner_id', 'amount_total', 'amount_due', 
                           'invoice_date', 'state', 'move_type']}
            )
            
            logger.info(f"Retrieved {len(invoices)} invoices")
            return invoices
            
        except Exception as e:
            logger.error(f"Error getting invoices: {e}")
            return []

    def get_payments(self, limit: int = 50) -> List[Dict]:
        """Get payments from Odoo"""
        if not self.models:
            return []
        
        try:
            payment_ids = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.payment',
                'search',
                [[]],
                {'limit': limit, 'order': 'date DESC'}
            )
            
            payments = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.payment',
                'read',
                [payment_ids],
                {'fields': ['name', 'partner_id', 'amount', 'date', 'state', 'payment_type']}
            )
            
            logger.info(f"Retrieved {len(payments)} payments")
            return payments
            
        except Exception as e:
            logger.error(f"Error getting payments: {e}")
            return []

    def get_account_balance(self) -> Dict:
        """Get current account balance"""
        if not self.models:
            return {'balance': 0, 'receivable': 0, 'payable': 0}
        
        try:
            # Get receivable accounts
            receivable_ids = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.account',
                'search',
                [[('account_type', '=', 'asset_receivable')]]
            )
            
            # Get payable accounts
            payable_ids = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.account',
                'search',
                [[('account_type', '=', 'liability_payable')]]
            )
            
            # Calculate balances
            receivable = 0
            payable = 0
            
            if receivable_ids:
                receivable_accounts = self.models.execute_kw(
                    self.config['db'],
                    self.uid,
                    self.config['password'],
                    'account.account',
                    'read',
                    [receivable_ids],
                    {'fields': ['balance']}
                )
                receivable = sum(acc.get('balance', 0) for acc in receivable_accounts)
            
            if payable_ids:
                payable_accounts = self.models.execute_kw(
                    self.config['db'],
                    self.uid,
                    self.config['password'],
                    'account.account',
                    'read',
                    [payable_ids],
                    {'fields': ['balance']}
                )
                payable = sum(acc.get('balance', 0) for acc in payable_accounts)
            
            balance = receivable - payable
            
            return {
                'balance': balance,
                'receivable': receivable,
                'payable': payable,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {'balance': 0, 'receivable': 0, 'payable': 0}

    def create_invoice(self, partner_name: str, amount: float, 
                      description: str, due_date: str = None) -> Optional[Dict]:
        """Create a new invoice"""
        if not self.models:
            return None
        
        try:
            # Find or create partner
            partner_ids = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'res.partner',
                'search',
                [[('name', '=', partner_name)]]
            )
            
            if not partner_ids:
                partner_id = self.models.execute_kw(
                    self.config['db'],
                    self.uid,
                    self.config['password'],
                    'res.partner',
                    'create',
                    [[{'name': partner_name}]]
                )
            else:
                partner_id = partner_ids[0]
            
            # Create invoice
            invoice_data = {
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }
            
            if due_date:
                invoice_data['invoice_date_due'] = due_date
            
            invoice_id = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'account.move',
                'create',
                [invoice_data]
            )
            
            logger.info(f"Created invoice {invoice_id}")
            return {'id': invoice_id, 'partner': partner_name, 'amount': amount}
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None

    def get_financial_summary(self, days: int = 30) -> Dict:
        """Get financial summary for the period"""
        invoices = self.get_invoices(limit=100)
        payments = self.get_payments(limit=100)
        balance = self.get_account_balance()
        
        # Filter by date
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_invoices = [
            inv for inv in invoices 
            if inv.get('invoice_date') and 
            datetime.strptime(inv['invoice_date'], '%Y-%m-%d') >= cutoff
        ]
        
        recent_payments = [
            pay for pay in payments
            if pay.get('date') and
            datetime.strptime(pay['date'], '%Y-%m-%d') >= cutoff
        ]
        
        total_revenue = sum(inv.get('amount_total', 0) for inv in recent_invoices 
                          if inv.get('state') == 'posted')
        total_received = sum(pay.get('amount', 0) for pay in recent_payments)
        
        return {
            'period_days': days,
            'total_invoices': len(recent_invoices),
            'total_revenue': total_revenue,
            'total_payments': len(recent_payments),
            'total_received': total_received,
            'outstanding': total_revenue - total_received,
            'current_balance': balance['balance'],
            'receivable': balance['receivable'],
            'payable': balance['payable'],
        }


def main():
    """Test Odoo connection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo Accounting Integration')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--summary', action='store_true', help='Get financial summary')
    parser.add_argument('--days', type=int, default=30, help='Days for summary')
    
    args = parser.parse_args()
    
    odoo = OdooAccounting(config_path=args.config)
    
    if args.test:
        print("\n" + "="*60)
        print("ODOO CONNECTION TEST")
        print("="*60)
        
        if odoo.uid:
            print(f"✓ Connected to Odoo: {odoo.config['url']}")
            print(f"  Database: {odoo.config['db']}")
            print(f"  User ID: {odoo.uid}")
            
            # Test get invoices
            invoices = odoo.get_invoices(limit=5)
            print(f"\n✓ Retrieved {len(invoices)} invoices")
            
            # Test get balance
            balance = odoo.get_account_balance()
            print(f"✓ Account Balance: ${balance['balance']:.2f}")
        else:
            print("✗ Failed to connect to Odoo")
            print(f"  URL: {odoo.config['url']}")
            print("  Check credentials and Odoo server status")
        
        print("="*60)
    
    if args.summary:
        print("\n" + "="*60)
        print(f"FINANCIAL SUMMARY (Last {args.days} days)")
        print("="*60)
        
        summary = odoo.get_financial_summary(days=args.days)
        
        print(f"Period: {summary['period_days']} days")
        print(f"Invoices: {summary['total_invoices']}")
        print(f"Revenue: ${summary['total_revenue']:.2f}")
        print(f"Payments Received: ${summary['total_received']:.2f}")
        print(f"Outstanding: ${summary['outstanding']:.2f}")
        print(f"Current Balance: ${summary['current_balance']:.2f}")
        
        print("="*60)


if __name__ == "__main__":
    main()
