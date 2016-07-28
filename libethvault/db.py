import app
import libethvault.email as em


def get_last_update_block():
    return app.BlockUpdate.query.order_by(app.BlockUpdate.last_block.desc()).first().last_block


def set_last_update_block(blk):
    app.db.session.add(app.BlockUpdate(blk))
    app.db.session.commit()


def get_email(vault_addr):
    v = app.Vault.query.filter_by(vault_addr=vault_addr).first()
    if v is None:
        raise KeyError

    if v.email is None:
        raise KeyError

    return v.email


def set_email(vault_addr, email_addr):
    old_email = app.Vault.query.filter_by(vault_addr=vault_addr).first()

    if old_email is None:
        raise ValueError

    try:
        if old_email.email != email_addr:
            em.send_to(old_email.email, "Alert: email address for vault {} has been changed to {}".format(vault_addr, email_addr),
                       "Contact change alert for vault {}".format(vault_addr))
            print "{}: {} -> {}".format(vault_addr, old_email.email, email_addr)
            old_email.email = email_addr
    except KeyError:
        em.send_to(email_addr, "Your email address has been registered for alerts from vault {}, owner {}.".format(
            vault_addr, old_email.owner
        ), "Registed email for vault {}".format(vault_addr))
        old_email.email = email_addr
        print "{}: () -> {}".format(vault_addr, email_addr)

    app.db.session.commit()


def get_owner(vault_addr):
    v = app.Vault.query.filter_by(vault_addr=vault_addr).first()
    return v.owner


def set_owner(vault_addr, owner_addr):
    app.db.session.add(app.Vault(vault_addr, owner_addr))
    app.db.session.commit()


def exists_vault(vault_addr):
    return app.Vault.query.filter_by(vault_addr=vault_addr).first() is not None


def exists_email(vault_addr):
    v = app.Vault.query.filter_by(vault_addr=vault_addr).first()
    return v is not None and v.email is not None


def get_vaults():
    result = app.Vault.query.all()
    result = [r.vault_addr for r in result]
    return result
