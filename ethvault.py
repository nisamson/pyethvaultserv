#! /usr/bin/env python
import json
import sys

import urllib3.contrib.pyopenssl
import os
import app as flsk
import libethvault.config as libconf
import libethvault.db as data
import libethvault.email as em
import libethvault.vault as vault

urllib3.contrib.pyopenssl.inject_into_urllib3()


def main(path_to_config_file):

    conf = None

    with open(path_to_config_file[0], "r") as config:
        conf = json.load(config)

    print "Config loaded."

    if "vault_registry" not in conf:
        raise ValueError("Need to know where the vault registry is!")

    libconf.set_config(conf)

    if not os.path.exists(libconf.CONFIG["db_loc"]):
        flsk.db.create_all()
        b = flsk.BlockUpdate(libconf.CONFIG["creation"])
        flsk.db.session.add(b)
        flsk.db.session.commit()

    poll_thread = vault.VaultPoller(libconf.CONFIG["loop_delay"])
    poll_thread.start()

    try:
        if libconf.CONFIG["key"] == "":
            flsk.app.run(port=80, threaded=True)
        else:
            context = (libconf.CONFIG["cert"], libconf.CONFIG["key"])
            flsk.app.run(port=80, threaded=True, ssl_context=context)
    finally:
        poll_thread.kill()
        poll_thread.wait_until_dead()
        em._mailpool.terminate()
        em._mailpool.join()

if __name__ == "__main__":
    main(sys.argv[1:])

