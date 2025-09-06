from spyne import ServiceBase, rpc
from models import (
    AccountSummary,
    CreateAccountRequest, CreateAccountResponse,
    ListAccountsRequest, ListAccountsResponse,
    GetBalanceRequest, GetBalanceResponse,
    DepositRequest, WithdrawRequest, MoneyActionResponse,
)
from db import SessionLocal
from db_models import User, Account, Session as DBSession

def _get_username_by_session(db, session_key: str):
    s = db.query(DBSession).filter(DBSession.session_key == session_key).first()
    return s.username if s else None

class AccountService(ServiceBase):

    @rpc(CreateAccountRequest, _returns=CreateAccountResponse)
    def create_account(ctx, req):
        db = SessionLocal()
        try:
            username = _get_username_by_session(db, req.session_key)
            if not username:
                return CreateAccountResponse(status=False, message="Invalid session", account=None)

            user = db.query(User).filter(User.username == username).first()
            if not user:
                return CreateAccountResponse(status=False, message="User not found", account=None)

            count = db.query(Account).filter(Account.owner_id == user.id).count()
            acc_id = f"ACC{count + 1:03d}"

            acc = Account(account_id=acc_id, balance=0, owner_id=user.id)
            db.add(acc)
            db.commit()

            return CreateAccountResponse(
                status=True,
                message="Account created",
                account=AccountSummary(account_id=acc.account_id, balance=acc.balance),
            )
        finally:
            db.close()

    @rpc(ListAccountsRequest, _returns=ListAccountsResponse)
    def list_accounts(ctx, req):
        db = SessionLocal()
        try:
            username = _get_username_by_session(db, req.session_key)
            if not username:
                return ListAccountsResponse(status=False, accounts=[])

            user = db.query(User).filter(User.username == username).first()
            if not user:
                return ListAccountsResponse(status=False, accounts=[])

            rows = db.query(Account).filter(Account.owner_id == user.id).all()
            data = [AccountSummary(account_id=a.account_id, balance=a.balance) for a in rows]
            return ListAccountsResponse(status=True, accounts=data)
        finally:
            db.close()

    @rpc(GetBalanceRequest, _returns=GetBalanceResponse)
    def get_balance(ctx, req):
        db = SessionLocal()
        try:
            username = _get_username_by_session(db, req.session_key)
            if not username:
                return GetBalanceResponse(status=False, message="Invalid session", account_id=req.account_id, balance=0)

            user = db.query(User).filter(User.username == username).first()
            if not user:
                return GetBalanceResponse(status=False, message="User not found", account_id=req.account_id, balance=0)

            acc = (db.query(Account)
                     .filter(Account.owner_id == user.id, Account.account_id == req.account_id)
                     .first())
            if not acc:
                return GetBalanceResponse(status=False, message="Account not found", account_id=req.account_id, balance=0)

            return GetBalanceResponse(status=True, message="OK", account_id=acc.account_id, balance=acc.balance)
        finally:
            db.close()

    @rpc(DepositRequest, _returns=MoneyActionResponse)
    def deposit(ctx, req):
        db = SessionLocal()
        try:
            username = _get_username_by_session(db, req.session_key)
            if not username:
                return MoneyActionResponse(status=False, message="Invalid session", account_id=req.account_id, balance=0)

            if req.amount is None or req.amount <= 0:
                return MoneyActionResponse(status=False, message="Amount must be > 0", account_id=req.account_id, balance=0)

            user = db.query(User).filter(User.username == username).first()
            acc = (db.query(Account)
                     .filter(Account.owner_id == user.id, Account.account_id == req.account_id)
                     .with_for_update()
                     .first())
            if not acc:
                return MoneyActionResponse(status=False, message="Account not found", account_id=req.account_id, balance=0)

            acc.balance += int(req.amount)
            db.commit()
            return MoneyActionResponse(status=True, message="Deposit OK", account_id=acc.account_id, balance=acc.balance)
        finally:
            db.close()

    @rpc(WithdrawRequest, _returns=MoneyActionResponse)
    def withdraw(ctx, req):
        db = SessionLocal()
        try:
            username = _get_username_by_session(db, req.session_key)
            if not username:
                return MoneyActionResponse(status=False, message="Invalid session", account_id=req.account_id, balance=0)

            if req.amount is None or req.amount <= 0:
                return MoneyActionResponse(status=False, message="Amount must be > 0", account_id=req.account_id, balance=0)

            user = db.query(User).filter(User.username == username).first()
            acc = (db.query(Account)
                     .filter(Account.owner_id == user.id, Account.account_id == req.account_id)
                     .with_for_update()
                     .first())
            if not acc:
                return MoneyActionResponse(status=False, message="Account not found", account_id=req.account_id, balance=0)

            amt = int(req.amount)
            if acc.balance < amt:
                return MoneyActionResponse(status=False, message="Insufficient funds", account_id=acc.account_id, balance=acc.balance)

            acc.balance -= amt
            db.commit()
            return MoneyActionResponse(status=True, message="Withdraw OK", account_id=acc.account_id, balance=acc.balance)
        finally:
            db.close()
