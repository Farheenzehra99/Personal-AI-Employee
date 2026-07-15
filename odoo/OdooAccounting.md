# Skill: OdooAccounting

## Purpose
Integrate with Odoo Community Edition for automated accounting, invoicing, and financial reporting.

## When to Use
- Track invoices and payments
- Generate financial reports
- Monitor accounts receivable/payable
- Reconcile bank transactions
- Create CEO Briefing revenue data

## Prerequisites

### Odoo Installation
1. Install Odoo Community Edition (v17+)
   - Local: Follow `ODOO_SETUP.md`
   - Docker: `docker run odoo:17.0`
   - Cloud VM: Oracle/AWS free tier

2. Install Accounting Module
   - Apps → Search "Accounting" → Install

3. Configure Company & Bank Accounts

### Python Dependencies
```bash
pip install xmlrpc
```

### Configuration
Create `odoo_config.json`:
```json
{
  "url": "http://localhost:8069",
  "db": "ai_employee",
  "username": "admin@example.com",
  "password": "your-password"
}
```

## Capabilities

### Invoice Management
- Create customer invoices
- Track invoice status (draft, posted, paid)
- Monitor outstanding payments
- Send payment reminders

### Payment Tracking
- Record customer payments
- Track payment methods
- Reconcile with invoices
- Generate payment reports

### Financial Reporting
- Account balances
- Profit & Loss statements
- Balance sheets
- Cash flow analysis

### Bank Integration
- Bank statement imports
- Automatic reconciliation
- Transaction categorization

## Usage

### Test Connection
```bash
python watchers/odoo_accounting.py --test
```

### Get Financial Summary
```bash
# Last 30 days
python watchers/odoo_accounting.py --summary --days 30

# Last 7 days
python watchers/odoo_accounting.py --summary --days 7
```

### Create Invoice
```
Use OdooAccounting to create invoice for Client ABC:
- Amount: $2,500
- Description: "Web Development Services - March 2026"
- Due Date: 2026-04-15
```

### Get Outstanding Invoices
```
Use OdooAccounting to list all unpaid invoices
```

### Generate Revenue Report
```
Use OdooAccounting to generate revenue report for Q1 2026
```

## Workflow

### Invoice Creation Flow

1. **Receive Request**
   - Client name
   - Amount
   - Description
   - Due date

2. **Create in Odoo**
   ```python
   odoo.create_invoice(
       partner_name="Client ABC",
       amount=2500.00,
       description="Services rendered",
       due_date="2026-04-15"
   )
   ```

3. **Save Confirmation**
   - Invoice number
   - PDF generation
   - Email to client (optional)

4. **Track Payment**
   - Monitor status
   - Send reminders if overdue
   - Reconcile when paid

### Financial Reporting Flow

1. **Collect Data**
   - All invoices for period
   - All payments received
   - Account balances

2. **Calculate Metrics**
   - Total revenue
   - Outstanding receivables
   - Net cash flow

3. **Generate Report**
   - Summary table
   - Charts (optional)
   - Insights

4. **Integrate with CEO Briefing**
   - Add to weekly briefing
   - Flag issues
   - Recommendations

## API Reference

### `get_invoices(limit=50, state=None)`
Get invoices from Odoo.

**Parameters:**
- `limit`: Max invoices to return
- `state`: Filter by state ('draft', 'posted', 'paid')

**Returns:** List of invoice dictionaries

### `get_payments(limit=50)`
Get payments from Odoo.

**Returns:** List of payment dictionaries

### `get_account_balance()`
Get current account balances.

**Returns:**
```json
{
  "balance": 15000.00,
  "receivable": 5000.00,
  "payable": 2000.00,
  "currency": "USD"
}
```

### `create_invoice(partner_name, amount, description, due_date=None)`
Create a new customer invoice.

**Returns:** Invoice dict with ID

### `get_financial_summary(days=30)`
Get financial summary for period.

**Returns:**
```json
{
  "period_days": 30,
  "total_invoices": 15,
  "total_revenue": 25000.00,
  "total_payments": 12,
  "total_received": 20000.00,
  "outstanding": 5000.00,
  "current_balance": 15000.00
}
```

## Example Output

### Financial Summary
```markdown
## Financial Overview (Last 30 Days)

| Metric | Value |
|--------|-------|
| Total Invoices | 15 |
| Revenue | $25,000 |
| Payments Received | $20,000 |
| Outstanding | $5,000 |
| Current Balance | $15,000 |

### Aging Report
| Age | Amount |
|-----|--------|
| Current | $3,000 |
| 1-30 days | $1,500 |
| 30-60 days | $500 |
| 60+ days | $0 |
```

## Integration

### With CEO Briefing
```python
# Get financial data for briefing
summary = odoo.get_financial_summary(days=7)

# Add to CEO Briefing
briefing += f"""
## Revenue This Week
- Invoices Sent: {summary['total_invoices']}
- Revenue: ${summary['total_revenue']:.2f}
- Outstanding: ${summary['outstanding']:.2f}
"""
```

### With Email
- Send invoices via email
- Payment reminders
- Use EmailResponder skill

### With Bank Sync
- Import bank statements
- Auto-reconcile payments
- Detect discrepancies

## Files
- Script: `watchers/odoo_accounting.py`
- Config: `odoo_config.json`
- Setup: `ODOO_SETUP.md`
- MCP: `watchers/odoo_mcp_server.py` (create)

## Troubleshooting

### Connection Failed
```bash
# Check Odoo is running
curl http://localhost:8069

# Check credentials
python watchers/odoo_accounting.py --test
```

### Module Not Found
```bash
# Install xmlrpc
pip install xmlrpc
```

### Authentication Error
- Verify username/password in config
- Check user has accounting permissions
- Reset password in Odoo if needed

## Best Practices

### Security
- Never commit `odoo_config.json` to git
- Use environment variables for credentials
- Enable HTTPS for production

### Performance
- Cache frequently accessed data
- Use appropriate limits on queries
- Schedule heavy operations off-peak

### Data Integrity
- Regular backups
- Reconcile monthly
- Audit trail for all transactions

## Related Skills
- CEOBriefingGenerator
- WeeklyBusinessAudit
- SubscriptionAuditor
- HumanApprovalRequest
