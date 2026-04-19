# envault

> CLI tool to securely store and sync environment variables across machines

---

## Installation

```bash
pip install envault
```

Or with pipx (recommended):

```bash
pipx install envault
```

---

## Usage

Initialize a vault in your project directory:

```bash
envault init
```

Add and retrieve environment variables:

```bash
# Store a variable
envault set DATABASE_URL "postgres://user:pass@localhost/db"

# Retrieve a variable
envault get DATABASE_URL

# List all stored variables
envault list

# Sync variables to a remote vault
envault push

# Pull variables on another machine
envault pull
```

Export variables to your current shell session:

```bash
eval $(envault export)
```

---

## How It Works

envault encrypts your environment variables locally using AES-256 and syncs them securely across machines via a remote backend. Each vault is protected by a master key that never leaves your device.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)