# Temperature sensor (server part)

This is a temperature sensor for baby bottles. The project consists of two parts: a temperature sensor [running on an Arduino](https://github.com/alexanderkoller/temperature_arduino/tree/main)
and a server written in Python. This repository is the server part.

Start as follows:

```
python main.py
```

## Requirements

```
apt install libsqlite3-dev
pip3 install -r requirements.txt
```

## Running on a Raspberry Pi

On a Raspberry Pi, compiling scipy from sources takes forever, if it
can be done at all. You can instead install a compiled package as
follows:

```
sudo apt-get install python3-scipy
```
