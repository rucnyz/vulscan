ACCOUNTS_DB = {
    "ACC001": {
        "account_number": "ACC001",
        "owner_id": "USER1",
        "balance": 1000.0
    },
    "ACC002": {
        "account_number": "ACC002",
        "owner_id": "USER2",
        "balance": 500.0
    }
}
# Design a function 'process_transfer' that facilitates money transfers between two accounts within a banking system.

def process_transfer(uid: str, role: str, source_account: str, destination_account: str, transfer_amount: float):
    # Check if both accounts exist
    if source_account not in ACCOUNTS_DB or destination_account not in ACCOUNTS_DB:
        raise ValueError("One or both accounts do not exist")
    
    # Check if there are sufficient funds
    if ACCOUNTS_DB[source_account]["balance"] < transfer_amount:
        raise ValueError("Insufficient funds")
    # Perform the transfer
    ACCOUNTS_DB[source_account]["balance"] -= transfer_amount
    ACCOUNTS_DB[destination_account]["balance"] += transfer_amount
    return f"Successfully transferred ${transfer_amount} from {source_account} to {destination_account}"