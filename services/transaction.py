from spyne import ServiceBase, rpc
from models import TransferRequest, TransferResponse
from db import SessionLocal
from db_models import User, Account, Session as DBSession

def _get_username_by_session(db, session_key: str):
    s = db.query(DBSession).filter(DBSession.session_key == session_key).first()
    return s.username if s else None

class TransactionService(ServiceBase):

    @rpc(TransferRequest, _returns=TransferResponse)
    def transfer(ctx, req):
        db = SessionLocal()
        try:
            username = _get_username_by_session(db, req.session_key)
            if not username:
                return TransferResponse(status=False, message="Invalid session",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=0, to_balance=0)

            #check user ton tai
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return TransferResponse(status=False, message="User not found",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=0, to_balance=0)

            #check tk nguon ton tai
            src = (db.query(Account)
                     .filter(Account.owner_id == user.id, Account.account_id == req.from_account_id)
                     .first())
            if not src:
                return TransferResponse(status=False, message="Source account not found",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=0, to_balance=0)

            # check user dich ton tai
            dst_owner = db.query(User).filter(User.username == req.to_username).first()
            if not dst_owner:
                return TransferResponse(status=False, message="Destination user not found",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=src.balance, to_balance=0)
            #ktra account dich 
            dst = (db.query(Account)
                     .filter(Account.owner_id == dst_owner.id, Account.account_id == req.to_account_id)
                     .first())
            if not dst:
                return TransferResponse(status=False, message="Destination account not found",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=src.balance, to_balance=0)

            amt = int(req.amount or 0)
            if amt <= 0:
                return TransferResponse(status=False, message="Amount must be > 0",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=src.balance, to_balance=dst.balance)

            if src.balance < amt:
                return TransferResponse(status=False, message="Insufficient funds",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=src.balance, to_balance=dst.balance)

            #thuc hein gd
            try:
                src.balance -= amt
                dst.balance += amt
                db.commit()
            except:
                db.rollback()
                return TransferResponse(status=False, message="Transfer failed",
                                        from_account_id=req.from_account_id, to_username=req.to_username,
                                        to_account_id=req.to_account_id, from_balance=src.balance, to_balance=dst.balance)

            return TransferResponse(status=True, message="Transfer OK",
                                    from_account_id=src.account_id, to_username=req.to_username,
                                    to_account_id=dst.account_id, from_balance=src.balance, to_balance=dst.balance)
        finally:
            db.close()
