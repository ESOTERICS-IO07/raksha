import json
import logging
from datetime import datetime, timezone
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../apps/api"))

from app.db.session import SessionLocal
from app.models.domain import User, Recipient, Transaction, FraudFlag, TransactionStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    db = SessionLocal()
    try:
        with open("data/seed/demo_graph.json", "r") as f:
            graph = json.load(f)

        # 1. Users
        users_added = 0
        for u in graph["users"]:
            if not db.query(User).filter(User.id == u["id"]).first():
                db.add(User(id=u["id"]))
                users_added += 1
        db.commit()

        # 2. Recipients
        recipients_added = 0
        for r in graph["recipients"]:
            if not db.query(Recipient).filter(Recipient.id == r["id"]).first():
                db.add(Recipient(id=r["id"]))
                recipients_added += 1
        db.commit()

        # 3. Fraud Flags
        flags_added = 0
        for f in graph["fraud_flags"]:
            if not db.query(FraudFlag).filter(FraudFlag.id == f["id"]).first():
                db.add(FraudFlag(id=f["id"], recipient_id=f["recipient_id"]))
                flags_added += 1
        db.commit()

        # 4. Transactions
        txs_added = 0
        for tx in graph["transactions"]:
            if not db.query(Transaction).filter(Transaction.id == tx["id"]).first():
                status_enum = getattr(TransactionStatus, tx["status"], TransactionStatus.PENDING)
                dt = datetime.fromisoformat(tx["timestamp"])
                db.add(Transaction(
                    id=tx["id"],
                    user_id=tx["user_id"],
                    recipient_id=tx["recipient_id"],
                    amount=tx["amount"],
                    currency=tx["currency"],
                    timestamp=dt,
                    device_id=tx["device_id"],
                    reason=tx["reason"],
                    status=status_enum
                ))
                txs_added += 1
        db.commit()

        logger.info("Seed successful!")
        logger.info(f"Users added: {users_added}")
        logger.info(f"Recipients added: {recipients_added}")
        logger.info(f"Fraud Flags added: {flags_added}")
        logger.info(f"Transactions added: {txs_added}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
