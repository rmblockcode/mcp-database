def calculate_installment_amounts(loan_amount: float, interest_rate: float, term_months: int):
    """
    Calculate monthly installment amounts using amortization formula
    
    Args:
        loan_amount: Total loan amount
        interest_rate: Annual interest rate (percentage)
        term_months: Loan term in months
    
    Returns:
        Tuple of (monthly_payment, principal_amount, interest_amount)
    """
    monthly_rate = (interest_rate / 100) / 12
    
    if monthly_rate == 0:
        monthly_payment = loan_amount / term_months
        return monthly_payment, monthly_payment, 0
    
    # Amortization formula
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / \
                     ((1 + monthly_rate) ** term_months - 1)
    
    return monthly_payment