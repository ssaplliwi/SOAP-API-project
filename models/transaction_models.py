from spyne import ComplexModel, Boolean, Unicode, Integer
from .common_base import TnsModel

class TransferRequest(TnsModel):
    session_key = Unicode
    from_account_id = Unicode
    to_username = Unicode
    to_account_id = Unicode
    amount = Integer

class TransferResponse(TnsModel):
    status = Boolean
    message = Unicode
    from_account_id = Unicode
    to_username = Unicode
    to_account_id = Unicode
    from_balance = Integer
    to_balance = Integer
