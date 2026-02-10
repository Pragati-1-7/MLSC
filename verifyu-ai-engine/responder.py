from algosdk.atomic_transaction_composer import AtomicTransactionComposer, AccountTransactionSigner
from algosdk import transaction, abi, account, mnemonic
import os
import config
import watcher

def get_signer():
    """
    Returns a TransactionSigner for the bot account.
    """
    # In production, use kmd or a secure vault. For hackathon, mnemonic in .env is fine.
    # We need to construct the private key from the mnemonic.
    try:
        if not os.getenv("BOT_MNEMONIC"):
             return None, None
        private_key = mnemonic.to_private_key(os.getenv("BOT_MNEMONIC"))
        signer = AccountTransactionSigner(private_key)
        return signer, account.address_from_private_key(private_key)
    except:
        return None, None

def trigger_emergency_poll(app_id, class_id):
    """
    Sends a transaction to the Smart Contract to trigger the poll.
    Method Signature: trigger_emergency_poll(string)void
    """
    client = watcher.get_algod_client()
    
    # Define the method we want to call
    # In a real app, load this from contract.json (ARC-4)
    method_def = abi.Method.from_signature("trigger_emergency_poll(string)void")
    
    # Get Account
    sender_mnemonic = os.getenv("BOT_MNEMONIC")
    if not sender_mnemonic:
        print("Error: BOT_MNEMONIC not set in .env")
        return None
        
    private_key = mnemonic.to_private_key(sender_mnemonic)
    sender_addr = account.address_from_private_key(private_key)
    
    # Get suggested params
    sp = client.suggested_params()
    
    # Create the interaction
    atc = AtomicTransactionComposer()
    signer = AccountTransactionSigner(private_key)
    
    atc.add_method_call(
        app_id=app_id,
        method=method_def,
        sender=sender_addr,
        sp=sp,
        signer=signer,
        method_args=[class_id]
    )
    
    try:
        result = atc.execute(client, 4)
        print(f"Transaction confirmed in round {result.confirmed_round}")
        return result.tx_ids[0]
    except Exception as e:
        print(f"Error submitting transaction: {e}")
        return None
