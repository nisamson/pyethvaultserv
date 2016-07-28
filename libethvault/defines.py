import hashlib
import sha3

# event VaultRegistered(address vault, address owner);
# event EmailRegistered(address vault, string email);

k = sha3.sha3_256()
k.update("VaultRegistered(address,address)")

VAULT_REGISTERED = "0x" + k.hexdigest()

# event Deposit(address sender, uint newAmount);
# event InitiateWithdrawal(uint newWithdrawalAmount, address newWithdrawAddress);
# event AbortWithdrawal(uint newWithdrawalAmount, address newWithdrawAddress);
# event Settled(uint newWithdrawalAmount, address newWithdrawAddress);

k = sha3.sha3_256()
k.update("Deposit(address,uint256)")

DEPOSIT = "0x" + k.hexdigest()

k = sha3.sha3_256()
k.update("InitiateWithdrawal(uint256,address)")

INITIATE_WITHDRAWL = "0x" + k.hexdigest()

k = sha3.sha3_256()
k.update("AbortWithdrawal(uint256,address)")

ABORT_WITHDRAWL = "0x" + k.hexdigest()

k = sha3.sha3_256()
k.update("Settled(uint256,address)")

SETTLED = "0x" + k.hexdigest()

k = sha3.sha3_256()
k.update("RegisteredEmail(bytes32,string)")

REGISTERED_EMAIL = "0x" + k.hexdigest()


VAULT_EVENTS = {DEPOSIT, INITIATE_WITHDRAWL, ABORT_WITHDRAWL, SETTLED, REGISTERED_EMAIL}