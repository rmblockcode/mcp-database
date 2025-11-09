import logging
from unittest import result
from fastmcp import FastMCP
from sqlalchemy import select
from .models import Loan, LoanInstallment
from .database import get_db_context

logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("Loan Management Server")

@mcp.tool
async def get_customer_loans(customer_id: str) -> str:
    """
    Get all loans for a specific customer using their customer ID.

    Args:
        customer_id: The unique identifier for the customer (e.g., CUST001)

    Returns:
        JSON string with loan details or error message
    """
    try:
        async with get_db_context() as session:
            result = await session.execute(
                select(Loan).filter(Loan.customer_id == customer_id)
            )
            loans = result.scalars().all()

            if not loans:
                return f"No loans found for customer ID: {customer_id}"

            loan_list = []

            for loan in loans:
                loan_list.append({
                    "loan_id": loan.id,
                    "customer_name": loan.customer_name,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "loan_term_months": loan.loan_term_months,
                    "start_date": str(loan.start_date),
                    "status": loan.status,
                    "remaining_balance": loan.remaining_balance
                })

            return str(loan_list)

    except Exception as e:
        logging.error(f"Error fetching loans for customer ID {customer_id}: {e}")
        return f"An error occurred while fetching loans for customer ID {customer_id}"


@mcp.tool
async def get_all_customers() -> str:
    """
    Get a list of all customers in the system
    
    Returns:
        JSON string with list of all customers and their IDs
    """
    try:
        async with get_db_context() as session:
            result = await session.execute(
                select(Loan.customer_id, Loan.customer_name)
                .distinct()
                .order_by(Loan.customer_name)
            )
            customers = result.all()
            
            if not customers:
                return "No customers found in the system"
            
            customer_list = []
            for customer in customers:
                customer_list.append({
                    "customer_id": customer.customer_id,
                    "customer_name": customer.customer_name
                })
            
            return str(customer_list)
    except Exception as e:
        logger.error(f"Error in get_all_customers: {e}")
        return f"Error retrieving customers: {str(e)}"


@mcp.tool
async def get_loan_installments(loan_id: int) -> str:
    """
    Get all installments for a specific loan
    
    Args:
        loan_id: The unique loan identifier
    
    Returns:
        JSON string with list of installments or error message
    """
    try:
        async with get_db_context() as session:
            # Get loan
            loan_result = await session.execute(
                select(Loan).filter(Loan.id == loan_id)
            )
            loan = loan_result.scalar_one_or_none()
            
            if not loan:
                return f"Loan not found with ID: {loan_id}"
            
            # Get installments
            installments_result = await session.execute(
                select(LoanInstallment)
                .filter(LoanInstallment.loan_id == loan_id)
                .order_by(LoanInstallment.installment_number)
            )
            installments = installments_result.scalars().all()
            
            if not installments:
                return f"No installments found for loan ID: {loan_id}"
            
            result_dict = {
                "loan_id": loan_id,
                "customer_name": loan.customer_name,
                "total_installments": len(installments),
                "installments": []
            }
            
            for inst in installments:
                result_dict["installments"].append({
                    "installment_id": inst.id,
                    "installment_number": inst.installment_number,
                    "due_date": str(inst.due_date),
                    "amount_due": inst.amount_due,
                    "principal_amount": inst.principal_amount,
                    "interest_amount": inst.interest_amount,
                    "amount_paid": inst.amount_paid,
                    "payment_date": str(inst.payment_date) if inst.payment_date else None,
                    "status": inst.status
                })
            
            return str(result_dict)
    except Exception as e:
        logger.error(f"Error in get_loan_installments: {e}")
        return f"Error retrieving installments: {str(e)}"


@mcp.tool
async def get_pending_installments(loan_id: int) -> str:
    """
    Get all pending (unpaid) installments for a specific loan
    
    Args:
        loan_id: The unique loan identifier
    
    Returns:
        JSON string with list of pending installments or error message
    """
    try:
        async with get_db_context() as session:
            # Get loan
            loan_result = await session.execute(
                select(Loan).filter(Loan.id == loan_id)
            )
            loan = loan_result.scalar_one_or_none()
            
            if not loan:
                return f"Loan not found with ID: {loan_id}"
            
            # Get pending installments
            installments_result = await session.execute(
                select(LoanInstallment)
                .filter(
                    LoanInstallment.loan_id == loan_id,
                    LoanInstallment.status.in_(["pending", "overdue", "partial"])
                )
                .order_by(LoanInstallment.due_date)
            )
            installments = installments_result.scalars().all()
            
            if not installments:
                return f"No pending installments for loan ID: {loan_id}"
            
            total_pending = sum(inst.amount_due - inst.amount_paid for inst in installments)
            
            result_dict = {
                "loan_id": loan_id,
                "customer_name": loan.customer_name,
                "total_pending_amount": round(total_pending, 2),
                "pending_installments": []
            }
            
            for inst in installments:
                result_dict["pending_installments"].append({
                    "installment_id": inst.id,
                    "installment_number": inst.installment_number,
                    "due_date": str(inst.due_date),
                    "amount_due": inst.amount_due,
                    "amount_paid": inst.amount_paid,
                    "remaining": round(inst.amount_due - inst.amount_paid, 2),
                    "status": inst.status
                })
            
            return str(result_dict)
    except Exception as e:
        logger.error(f"Error in get_pending_installments: {e}")
        return f"Error retrieving pending installments: {str(e)}"


@mcp.tool
async def get_overdue_installments(customer_id: str) -> str:
    """
    Get all overdue installments for a specific customer across all their loans
    
    Args:
        customer_id: The unique customer identifier
    
    Returns:
        JSON string with list of overdue installments or error message
    """
    try:
        async with get_db_context() as session:
            # Get customer loans
            loans_result = await session.execute(
                select(Loan).filter(Loan.customer_id == customer_id)
            )
            loans = loans_result.scalars().all()
            
            if not loans:
                return f"No loans found for customer ID: {customer_id}"
            
            loan_ids = [loan.id for loan in loans]
            
            # Get overdue installments
            installments_result = await session.execute(
                select(LoanInstallment)
                .filter(
                    LoanInstallment.loan_id.in_(loan_ids),
                    LoanInstallment.status == "overdue"
                )
                .order_by(LoanInstallment.due_date)
            )
            overdue_installments = installments_result.scalars().all()
            
            if not overdue_installments:
                return f"No overdue installments for customer ID: {customer_id}"
            
            total_overdue = sum(inst.amount_due - inst.amount_paid for inst in overdue_installments)
            
            result_dict = {
                "customer_id": customer_id,
                "customer_name": loans[0].customer_name,
                "total_overdue_amount": round(total_overdue, 2),
                "overdue_count": len(overdue_installments),
                "overdue_installments": []
            }
            
            for inst in overdue_installments:
                result_dict["overdue_installments"].append({
                    "installment_id": inst.id,
                    "loan_id": inst.loan_id,
                    "installment_number": inst.installment_number,
                    "due_date": str(inst.due_date),
                    "amount_due": inst.amount_due,
                    "days_overdue": (datetime.now().date() - inst.due_date).days,
                    "status": inst.status
                })
            
            return str(result_dict)
    except Exception as e:
        logger.error(f"Error in get_overdue_installments: {e}")
        return f"Error retrieving overdue installments: {str(e)}"


@mcp.tool
async def get_customer_summary(customer_name: str) -> str:
    """
    Get a complete summary of a customer's loans and installments by name
    This is a convenience tool that searches by name and returns all relevant information
    
    Args:
        customer_name: The customer name to search for (partial match supported)
    
    Returns:
        JSON string with complete customer summary including loans and installment status
    """
    try:
        async with get_db_context() as session:
            # Search for customer
            customer_result = await session.execute(
                select(Loan.customer_id, Loan.customer_name)
                .filter(Loan.customer_name.ilike(f"%{customer_name}%"))
                .distinct()
                .limit(1)
            )
            customer = customer_result.first()
            
            if not customer:
                return f"No customer found matching name: {customer_name}"
            
            customer_id = customer.customer_id
            customer_full_name = customer.customer_name
            
            # Get all loans for this customer
            loans_result = await session.execute(
                select(Loan).filter(Loan.customer_id == customer_id)
            )
            loans = loans_result.scalars().all()
            
            if not loans:
                return f"No loans found for customer: {customer_full_name}"
            
            # Calculate totals
            total_loan_amount = sum(loan.loan_amount for loan in loans)
            total_remaining = sum(loan.remaining_balance for loan in loans)
            active_loans_count = sum(1 for loan in loans if loan.status == "active")
            
            # Get installment statistics
            loan_ids = [loan.id for loan in loans]
            
            # Pending installments
            pending_result = await session.execute(
                select(LoanInstallment)
                .filter(
                    LoanInstallment.loan_id.in_(loan_ids),
                    LoanInstallment.status.in_(["pending", "overdue", "partial"])
                )
            )
            pending_installments = pending_result.scalars().all()
            total_pending = sum(inst.amount_due - inst.amount_paid for inst in pending_installments)
            
            # Overdue installments
            overdue_result = await session.execute(
                select(LoanInstallment)
                .filter(
                    LoanInstallment.loan_id.in_(loan_ids),
                    LoanInstallment.status == "overdue"
                )
            )
            overdue_installments = overdue_result.scalars().all()
            total_overdue = sum(inst.amount_due - inst.amount_paid for inst in overdue_installments)
            
            # Paid installments
            paid_result = await session.execute(
                select(LoanInstallment)
                .filter(
                    LoanInstallment.loan_id.in_(loan_ids),
                    LoanInstallment.status == "paid"
                )
            )
            paid_installments = paid_result.scalars().all()
            total_paid = sum(inst.amount_paid for inst in paid_installments)
            
            # Build loan details
            loan_details = []
            for loan in loans:
                loan_details.append({
                    "loan_id": loan.id,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "loan_term_months": loan.loan_term_months,
                    "start_date": str(loan.start_date),
                    "status": loan.status,
                    "remaining_balance": loan.remaining_balance
                })
            
            result_dict = {
                "customer_id": customer_id,
                "customer_name": customer_full_name,
                "summary": {
                    "total_loans": len(loans),
                    "active_loans": active_loans_count,
                    "total_loan_amount": round(total_loan_amount, 2),
                    "total_remaining_balance": round(total_remaining, 2),
                    "total_paid": round(total_paid, 2),
                    "total_pending_amount": round(total_pending, 2),
                    "total_overdue_amount": round(total_overdue, 2),
                    "overdue_installments_count": len(overdue_installments),
                    "pending_installments_count": len(pending_installments)
                },
                "loans": loan_details
            }
            
            return str(result_dict)
    except Exception as e:
        logger.error(f"Error in get_customer_summary: {e}")
        return f"Error retrieving customer summary: {str(e)}"