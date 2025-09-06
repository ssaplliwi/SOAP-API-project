from spyne import ComplexModel, Boolean, Unicode, Integer
from spyne.model.complex import Array
from .common_base import TnsModel

#model account
class AccountSummary(TnsModel):
    account_id = Unicode
    balance = Integer

class CreateAccountRequest(TnsModel):
    session_key = Unicode

class CreateAccountResponse(TnsModel):
    status = Boolean
    message = Unicode
    account = AccountSummary.customize(nullable=True) #cho phep null de tranh loi serilize neu co

class ListAccountsRequest(TnsModel):
    session_key = Unicode

class ListAccountsResponse(TnsModel):
    status = Boolean
    accounts = Array(AccountSummary)

class GetBalanceRequest(TnsModel):
    session_key = Unicode
    account_id = Unicode

class GetBalanceResponse(TnsModel):
    status = Boolean
    message = Unicode
    account_id = Unicode
    balance = Integer

class DepositRequest(TnsModel):
    session_key = Unicode
    account_id = Unicode
    amount = Integer

class WithdrawRequest(TnsModel):
    session_key = Unicode
    account_id = Unicode
    amount = Integer

class MoneyActionResponse(TnsModel):
    status = Boolean
    message = Unicode
    account_id = Unicode
    balance = Integer
