import libethvault.config as config
from ethjsonrpc import EthJsonRpc
import subprocess
import libethvault.db as data
import libethvault.defines as defines
import libethvault.email as email
from threading import Thread, Lock, Condition
import json
import time

_rpc = None
_filter_id = None


def start_rpc():
    global _rpc

    _rpc = EthJsonRpc("127.0.0.1", config.CONFIG["rpc_port"])
    try:
        _rpc.eth_blockNumber()
    except:
        print "Couldn't connect to geth. RPC not started?"
        print "Checking to see if geth node is active..."

        try:
            subprocess.check_call(["pgrep", "geth"])
        except subprocess.CalledProcessError:
            print "Geth does not appear to be running."
        else:
            print "Geth appears to be running, but we cannot connect."

        raise IOError("Could not connect to geth instance.")

    addrs = [config.CONFIG["vault_registry"]]
    addrs.extend(data.get_vaults())
    filter_id = _rpc.eth_newFilter(
            from_block=data.get_last_update_block(),
            to_block="latest" ,
            address=addrs)

    global _filter_id
    _filter_id = filter_id


def needs_rpc(func):

    def wrapper(*args, **kwargs):
        if _rpc is None:
            start_rpc()
        return func(*args, **kwargs)

    return wrapper


@needs_rpc
def get_new_events():

    global _filter_id
    old_block = data.get_last_update_block()
    current_block = _rpc.eth_blockNumber()
    if old_block == current_block:
        return
    ret = _rpc.eth_getFilterLogs(_filter_id)
    if ret is None:
        return
    new_events = ret # json.loads(ret)

    addrs_updated = False

    for event_obj in new_events:
        if "removed" in event_obj and event_obj["removed"] == "true":
            continue

        data_arr = event_obj["data"]

        topic = event_obj["topics"][0]

        if topic == defines.VAULT_REGISTERED\
                and event_obj["address"].lower() == config.CONFIG["vault_registry"].lower():
            # event VaultRegistered(address vault, address owner);

            vault_addr = "0x" + data_arr[2 + 24:2 + 24 + 40]
            if data.exists_vault(vault_addr):
                continue

            owner_addr = "0x" + data_arr[-40:]
            print "New Vault: {} -> {}".format(vault_addr, owner_addr)
            data.set_owner(vault_addr, owner_addr)
            addrs_updated = True

        elif topic == defines.REGISTERED_EMAIL:
            vault_addr = event_obj["address"]
            email_addr = data_arr[2 + 64 + 64 + 64:].rstrip('0').decode('hex')

            if not data.exists_vault(vault_addr):
                continue

            data.set_email(vault_addr, email_addr)
        elif topic == defines.INITIATE_WITHDRAWL:
            vault_addr = event_obj["address"]

            if not data.exists_vault(vault_addr)\
                    or not data.exists_email(vault_addr):
                continue

            email_addr = data.get_email(vault_addr)
            print "Sending withdrawl alert to {}".format(email_addr)
            amount = data_arr[:2 + 64]
            dest_addr = "0x" + data_arr[2 + 64 + 24:]

            email.send_alert_to(email_addr, vault_addr, amount, dest_addr)

    if addrs_updated:
        addrs = [config.CONFIG["vault_registry"]]
        addrs.extend(data.get_vaults())
        _filter_id = _rpc.eth_newFilter(from_block=old_block, to_block="latest"
                                        ,address=addrs)
    else:
        data.set_last_update_block(current_block)
        addrs = [config.CONFIG["vault_registry"]]
        addrs.extend(data.get_vaults())

        _filter_id = _rpc.eth_newFilter(from_block=current_block, to_block="latest"
                                        ,address=addrs)


class VaultPoller(Thread):

    def __init__(self, loop_delay):
        super(VaultPoller, self).__init__()
        self.lock = Lock()
        self.killed = Condition(self.lock)
        self._kill = False
        self._dead = False
        self.loop_delay = loop_delay

    def kill(self):
        with self.lock:
            print "Killed worker thread."
            self._kill = True
            self.killed.notify_all()

    def wait_until_dead(self):
        with self.lock:
            if not self._kill:
                raise ValueError("Cannot wait for thread to die: thread not wounded (with self.kill()).")

            while not self._dead:
                self.killed.wait()

    def run(self):
        cnt = 0
        while True:
            with self.lock:
                if self._kill:
                    print "Received kill signal."
                    self._dead = True
                    self.killed.notify_all()
                    return

            print "Polling for new events {}".format(cnt)
            cnt += 1
            get_new_events()
            print "Done polling. {}".format(cnt - 1)

            with self.lock:
                self.killed.wait(self.loop_delay)




