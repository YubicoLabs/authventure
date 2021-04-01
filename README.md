# Authventure by Yubico

Authventure is a brand new way to experience your YubiKey, brought to you by Yubico.

For best results, we recommend https://github.com/Swordfish90/cool-retro-term


## Is this a joke?
Well, yes and no. We did create this for April Fools. For us this was a fun
side-project we could work on together as a team, despite all working from
home. We had a blast creating it, and we hope it brought some smiles to some
faces. Now, we DID create a fully functional program which DOES allow you to
extract TOTP codes from your YubiKey, just like in the video. You absolutely
CAN use this to log in to services (though we also offer [other
tools](https://www.yubico.com/products/yubico-authenticator/) for that, if
adventuring isn't your thing).


## Behind the scenes
The `authventure.py` file in this repository contains the entire program, but
all the heavy lifting (communicating with the YubiKey, implementation of the
OATH TOTP protocol, etc.) is done by
[yubikey-manager](https://github.com/Yubico/yubikey-manager). Besides providing
a command line tool for configuring your YubiKey, it can also be used as a
Python library for programatically interfacing with the various applications on
a YubiKey. This allows you to write scripts to configure your YubiKey, or even
full adventure games!


## Prerequisites
To use `authventure` you'll need [a YubiKey](https://www.yubico.com/store/)
with OATH functionality, such as one of the YubiKey 5 models. You'll also need
to have at least one OATH credential provisioned.


### Running from CI binaries
Pre-compiled binaries for Windows, Mac and Linux are downloadable from the
Actions tab on this project page on Github (note that you must be logged in to
GitHub for those to be available).


### Installation from source
1. Clone the repository.
```
$ git clone https://github.com/YubicoLabs/authventure.git
```
2. (optional) Create a virtualenv:
```
$ virtualenv .venv
$ source .venv/bin/activate
```
3. Install requirements:
```
$ pip install -r requirements.txt
```
4. Run the application:
```
$ python authventure.py
```
