# Python Ethereum Vault Server

The backend for the Ethereum vault project. Designed to monitor the blockchain for events relating to Ethereum vaults.

Created for the IC3 Ethereum Bootcamp in July 2016.

## Installation

You must have an email server available at port 9267 for email to work.
The `simple_smtp.py` script can act as a dummy server for this purpose.

`pip install -r requirements.txt`

## Usage

`python ./ethvault.py <config-file>`

The config file is a json file which should contain a JSON object which looks like the dict in
`config.py`.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License

