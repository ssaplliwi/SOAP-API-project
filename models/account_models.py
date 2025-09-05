from spyne import ComplexModel, Boolean, Unicode, Integer
from spyne.model.complex import Array

#model cho account
class Account(ComplexModel):
    id = Unicode
    balance = Integer

class CreateAccountResponse(ComplexModel):
    status = Boolean
    message = Unicode
    account = Account.customize(nullable=True) #cho phep sd None (co the tranh loi serialize)

class GetAccountResponse(ComplexModel):
    status = Boolean
    accounts = Array(Account)

class GetBalanceResponse(ComplexModel):
    status = Boolean
    message = Unicode
    account_id = Unicode
    balance = Integer

#model cho nap, rut
class MoneyActionResponse(ComplexModel):
    status = Boolean
    message = Unicode
    account_id = Unicode
    balance = Integer

#model transfer
class TransferResponse(ComplexModel):
    status = Boolean
    message = Unicode
    from_account_id = Unicode
    to_username = Unicode
    to_account_id = Unicode
    from_balance = Integer
    to_balance = Integer
    