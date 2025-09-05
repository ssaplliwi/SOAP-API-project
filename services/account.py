from spyne import ServiceBase, rpc, Unicode, Integer
from models.account_models import (
    Account, CreateAccountResponse, GetAccountResponse,
    GetBalanceResponse, MoneyActionResponse, TransferResponse
)
from storage.memory import sessions, accounts

class AccountService(ServiceBase):
    @rpc(Unicode, _returns=CreateAccountResponse)
    def create_account(ctx, session_key):
        username = sessions.get(session_key)
        if not username:
            return CreateAccountResponse(status=False, message="Invalid session", account=None)
        
        next_idx = len(accounts.get(username, [])) + 1 #neu user chua co account thi tra ve rong (TH chua tao)
        acc_id = f"ACC{next_idx:03d}"
        account = {"id": acc_id, "balance" : 0}
        accounts.setdefault(username, []).append(account)

        return CreateAccountResponse(status=True, message="Account created", account=Account(id=acc_id, balance=0))

    @rpc(Unicode, _returns=GetAccountResponse)
    def get_accounts(ctx, session_key):
        username = sessions.get(session_key)
        if not username:
            return GetAccountResponse(status=False, accounts=[])

        accs = [Account(id=a["id"], balance=a["balance"]) for a in accounts.get(username, [])]
        return GetAccountResponse(status=True, accounts=accs)

    @rpc(Unicode, Unicode, _returns=GetBalanceResponse)
    def get_balance(ctx, session_key, account_id):
        username = sessions.get(session_key)
        if not username:
            return GetBalanceResponse(status=False, message="Invalid session", account_id=account_id, balance=0)
        
        for a in accounts.get(username, []):
            if a["id"] == account_id:
                return GetBalanceResponse(status=True, message="OK", account_id=account_id, balance=a["balance"])

        return GetBalanceResponse(status=False, message="Account not found", account_id=account_id, balance=0)

#api cho nap, rut
    @rpc(Unicode, Unicode, Integer, _returns=MoneyActionResponse)
    def deposit(ctx, session_key, account_id, amount):
        username = sessions.get(session_key)
        if not username:
            return MoneyActionResponse(status=False, message="Invalid session", account_id=account_id, balance=0)
        
        if amount is None or amount <= 0:
            return MoneyActionResponse(status=False, message="Amount must be > 0", account_id=account_id, balance=0)
        
        for a in accounts.get(username, []):
            if a["id"] == account_id:
                a["balance"] += int(amount)
                return MoneyActionResponse(status=True, message="Deposit OK", account_id=account_id, balance=a["balance"])
            
        return MoneyActionResponse(status=False, message="Account not found", account_id=account_id, balance=0)

    @rpc(Unicode, Unicode, Integer, _returns=MoneyActionResponse)
    def withdraw(ctx, session_key, account_id, amount):
        username = sessions.get(session_key)
        if not username:
            return MoneyActionResponse(status=False, message="Invalid session", account_id=account_id, balance=0)

        if amount is None or amount <= 0:
            return MoneyActionResponse(status=False, message="Amount must be > 0", account_id=account_id, balance=0)
        
        for a in accounts.get(username, []):
            if a["id"] == account_id:
                if a["balance"] < int(amount):
                    return MoneyActionResponse(status=False, message="Insufficient funds", account_id=account_id, balance=a["balance"])
                a["balance"] -= int(amount)
                return MoneyActionResponse(status=True, message="Withdraw OK", account_id=account_id, balance=a["balance"])

        return MoneyActionResponse(status=False, message="Account not found", account_id=account_id, balance=0)

#api transfer
    @rpc(Unicode, Unicode, Unicode, Unicode, Integer, _returns=TransferResponse)
    def transfer(ctx, session_key, from_account_id, to_username, to_account_id, amount):
        #ktra phien hien tai
        username = sessions.get(session_key)
        if not username:
            return TransferResponse(status=False, message="Invalid session"
                                    , from_account_id=from_account_id, to_username=to_username
                                    , to_account_id=to_account_id, from_balance=0, to_balance=0
            )

        if not from_account_id or not to_username or not to_account_id:
            return TransferResponse(status=False, message="Missing parameters"
                                    , from_account_id=from_account_id, to_username=to_username
                                    , to_account_id=to_account_id, from_balance=0, to_balance=0
            )
        
        if amount is None or amount <= 0:
            return TransferResponse(status=False, message="Amount must be > 0"
                                    , from_account_id=from_account_id, to_username=to_username
                                    , to_account_id=to_account_id, from_balance=0, to_balance=0
            )
        #ktra tai khoan nguon co ton tai vs user(phien) hien tai
        src = None
        for a in accounts.get(username, []):
            if a["id"] == from_account_id:
                src = a
                break
        if src is None:
            return TransferResponse(
                status=False, message="Source account not found", from_account_id=from_account_id
                , to_username=to_username, to_account_id=to_account_id, from_balance=0, to_balance=0
            )
        
        #ktra account dich
        dst = None
        for a in accounts.get(to_username, []):
            if a["id"] == to_account_id:
                dst = a
                break
        if dst is None:
            return TransferResponse(
                status=False, message="Destination account not found", from_account_id=from_account_id
                , to_username=to_username, to_account_id=to_account_id, from_balance=src["balance"], to_balance=0
            )

        #ktra so du tk nguon
        amt = int(amount)
        if src["balance"] < amt:
            return TransferResponse(
                status=False, message="Insufficient funds", from_account_id=from_account_id
                , to_username=to_username, to_account_id=to_account_id, from_balance=src["balance"], to_balance=dst["balance"]
            )

        src["balance"] -= amt
        dst["balance"] += amt

        return TransferResponse(
            status=True, message="Transfer OK", from_account_id=from_account_id, to_username=to_username
            , to_account_id=to_account_id, from_balance=src["balance"], to_balance=dst["balance"]
        )
