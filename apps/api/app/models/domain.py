from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ALLOWED = "ALLOWED"
    CANCELLED = "CANCELLED"
    HELD = "HELD"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="user")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user")
    behavior_profile: Mapped[Optional["BehaviorProfile"]] = relationship("BehaviorProfile", back_populates="user", uselist=False)

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship("User", back_populates="accounts")

class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="recipient")
    fraud_flags: Mapped[List["FraudFlag"]] = relationship("FraudFlag", back_populates="recipient")
    fraud_cluster: Mapped[Optional["FraudCluster"]] = relationship("FraudCluster", back_populates="recipient", uselist=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4))
    currency: Mapped[str] = mapped_column(String(3))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    recipient: Mapped["Recipient"] = relationship("Recipient", back_populates="transactions")
    signals: Mapped[List["TransactionSignal"]] = relationship("TransactionSignal", back_populates="transaction")
    intent_result: Mapped[Optional["IntentResult"]] = relationship("IntentResult", back_populates="transaction", uselist=False)
    risk_assessment: Mapped[Optional["RiskAssessment"]] = relationship("RiskAssessment", back_populates="transaction", uselist=False)
    friction_decision: Mapped[Optional["FrictionDecision"]] = relationship("FrictionDecision", back_populates="transaction", uselist=False)
    audit_events: Mapped[List["AuditEvent"]] = relationship("AuditEvent", back_populates="transaction")

class TransactionSignal(Base):
    __tablename__ = "transaction_signals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="signals")

class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    
    user: Mapped["User"] = relationship("User", back_populates="behavior_profile")

class IntentResult(Base):
    __tablename__ = "intent_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), unique=True)
    
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="intent_result")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), unique=True)
    
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="risk_assessment")

class FrictionDecision(Base):
    __tablename__ = "friction_decisions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), unique=True)
    
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="friction_decision")

class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id"))
    
    recipient: Mapped["Recipient"] = relationship("Recipient", back_populates="fraud_flags")

class FraudCluster(Base):
    __tablename__ = "fraud_clusters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id"), unique=True)
    
    recipient: Mapped["Recipient"] = relationship("Recipient", back_populates="fraud_cluster")

class ScenarioDefinition(Base):
    __tablename__ = "scenario_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    event_type: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="audit_events")
