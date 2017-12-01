halite
======

My bot for [halite.io](https://halite.io/).

---

## Configuration

Generate a Halite API key from [here](https://halite.io/user/settings).

## Usage

Authenticate with Halite:
```bash
hlt auth
```

Package up the bot:
```bash
pushd bot; zip -r ../bot.zip .; popd
```

Upload the latest version:
```bash
hlt bot -b bot.zip
```
