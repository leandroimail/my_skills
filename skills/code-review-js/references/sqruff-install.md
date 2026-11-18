# Installing sqruff

`sqruff` is a fast SQL linter/formatter built in Rust. There is **no npm
package** — install it per OS (verified against v0.39.0):

## macOS

```bash
brew install sqruff
```

## Linux

Prebuilt musl binaries (no glibc dependency):

```bash
curl -fsSL https://github.com/quarylabs/sqruff/releases/latest/download/sqruff-linux-x86_64-musl.tar.gz \
  | tar -xz -C /usr/local/bin sqruff
# ARM: use sqruff-linux-aarch64-musl.tar.gz
```

## Windows

Download `sqruff-windows-x86_64.zip` from the
[latest release](https://github.com/quarylabs/sqruff/releases/latest),
extract, and add the folder to `PATH`.

## Any OS (fallbacks)

```bash
pip install sqruff       # published on PyPI — handy in CI images with Python
cargo install sqruff     # builds from source (Rust toolchain required)
```

## Verify

```bash
sqruff --version
sqruff lint --dialect ansi queries/
```

Official docs and release assets: https://github.com/quarylabs/sqruff
