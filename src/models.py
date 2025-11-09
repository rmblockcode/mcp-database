# models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Loan(Base):
    """
    Loan table model representing customer loans
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True, nullable=False)
    customer_name = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    loan_term_months = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # active, paid, defaulted
    remaining_balance = Column(Float, nullable=False)
    
    # Relationship with installments
    installments = relationship(
        "LoanInstallment",
        back_populates="loan",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Loan(id={self.id}, customer_id={self.customer_id}, amount={self.loan_amount})>"


class LoanInstallment(Base):
    """
    Loan installment table model representing individual payment installments
    """
    __tablename__ = "loan_installments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    installment_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    due_date = Column(Date, nullable=False)
    amount_due = Column(Float, nullable=False)
    principal_amount = Column(Float, nullable=False)
    interest_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    payment_date = Column(Date, nullable=True)
    status = Column(String, nullable=False)  # pending, paid, overdue, partial
    
    # Relationship with loan
    loan = relationship("Loan", back_populates="installments")

    def __repr__(self):
        return f"<LoanInstallment(id={self.id}, loan_id={self.loan_id}, number={self.installment_number})>"
