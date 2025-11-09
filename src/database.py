# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from .utils import calculate_installment_amounts
import os
import logging

logger = logging.getLogger(__name__)

# Database URL configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/loans_db"
)
POOL_SIZE = int(os.getenv("POOL_SIZE", 20))
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

# Global engine variable
engine = None
AsyncSessionLocal = None


def get_engine():
    """Get or create the database engine"""
    global engine
    if engine is None:
        engine = create_async_engine(
            DATABASE_URL,
            echo=DATABASE_ECHO,
            pool_size=POOL_SIZE,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
        )
    return engine


def get_session_factory():
    """Get or create the session factory"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return AsyncSessionLocal


async def init_db():
    """Initialize database - create tables and seed sample data"""
    # Import all models to register them with SQLAlchemy
    from .models import Base, Loan, LoanInstallment
    from sqlalchemy import select
    
    logger.info("Initializing database...")
    
    # Initialize engine and session factory
    engine = get_engine()
    session_factory = get_session_factory()
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    # Check if data already exists and seed if needed
    async with session_factory() as session:
        try:
            # Check if loans already exist
            result = await session.execute(select(Loan).limit(1))
            existing_loan = result.scalar_one_or_none()
            
            if existing_loan:
                logger.info("Database already contains data, skipping seed")
                return
            
            logger.info("Seeding database with sample data...")
            
            # Create sample loans
            sample_loans = [
                Loan(
                    customer_id="CUST001",
                    customer_name="John Doe",
                    loan_amount=50000.00,
                    interest_rate=5.5,
                    loan_term_months=60,
                    start_date=datetime(2025, 1, 15).date(),
                    status="active",
                    remaining_balance=35000.00
                ),
                Loan(
                    customer_id="CUST002",
                    customer_name="Jane Smith",
                    loan_amount=25000.00,
                    interest_rate=4.8,
                    loan_term_months=36,
                    start_date=datetime(2025, 6, 1).date(),
                    status="active",
                    remaining_balance=18000.00
                ),
                Loan(
                    customer_id="CUST003",
                    customer_name="Bob Johnson",
                    loan_amount=100000.00,
                    interest_rate=6.2,
                    loan_term_months=120,
                    start_date=datetime(2024, 3, 10).date(),
                    status="active",
                    remaining_balance=85000.00
                ),
            ]
            
            # Add loans to session
            for loan in sample_loans:
                session.add(loan)
            
            # Flush to get loan IDs
            await session.flush()
            
            logger.info(f"Created {len(sample_loans)} sample loans")
            
            # Generate installments for each loan
            installment_count = 0
            for loan in sample_loans:
                monthly_payment = calculate_installment_amounts(
                    loan.loan_amount,
                    loan.interest_rate,
                    loan.loan_term_months
                )
                
                remaining_principal = loan.loan_amount
                current_date = loan.start_date
                
                for i in range(1, loan.loan_term_months + 1):
                    # Calculate due date (monthly)
                    due_date = current_date + timedelta(days=30 * i)
                    
                    # Calculate interest and principal for this installment
                    monthly_rate = (loan.interest_rate / 100) / 12
                    interest_amount = remaining_principal * monthly_rate
                    principal_amount = monthly_payment - interest_amount
                    
                    # Determine status (simulate some payments)
                    if i <= 15:  # First 15 installments are paid
                        status = "paid"
                        amount_paid = monthly_payment
                        payment_date = due_date - timedelta(days=2)
                    elif i == 16 and loan.customer_id == "CUST003":  # One overdue
                        status = "overdue"
                        amount_paid = 0.0
                        payment_date = None
                    else:
                        status = "pending"
                        amount_paid = 0.0
                        payment_date = None
                    
                    installment = LoanInstallment(
                        loan_id=loan.id,
                        installment_number=i,
                        due_date=due_date,
                        amount_due=round(monthly_payment, 2),
                        principal_amount=round(principal_amount, 2),
                        interest_amount=round(interest_amount, 2),
                        amount_paid=round(amount_paid, 2),
                        payment_date=payment_date,
                        status=status
                    )
                    
                    session.add(installment)
                    remaining_principal -= principal_amount
                    installment_count += 1
            
            # Commit all changes
            await session.commit()
            logger.info(f"Created {installment_count} installments for all loans")
            logger.info("Database seeding completed successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {e}")
            raise


@asynccontextmanager
async def get_db_context():
    """Context manager for database sessions"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connections"""
    global engine, AsyncSessionLocal
    if engine:
        await engine.dispose()
        engine = None
        AsyncSessionLocal = None
        logger.info("Database connections closed")