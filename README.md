# PKPD: pharmacokinetics simplified
[![Build Status](https://travis-ci.org/SABS-R3-projects/PKPD.svg?branch=master)](https://travis-ci.org/SABS-R3-projects/PKPD)

PKPD is a graphical interface for pharmacokinetic and (work in progress) pharmacodynamic modelling. It's for people who want to model pharmacological metabolism without having to touch any code!

## Quickstart

PKPD requires python 3.6+ and [myokit](http://myokit.org). To get started, git clone the repository and run the setup.py to install it as a python module. The interface can then be called from the terminal or command line using `python -m PKPD`.

## In-depth installation guide

This guide is split into sections:-  
A) Install python  
B) Install myokit  
C) Install git  
D) Install PKPD  
E) Use PKPD  
F) Troubleshooting  

### A) How to install Python
1. Open a terminal (iOS or ubuntu: search your apps for 'terminal') or command line (windows: open start menu & search 'cmd').
2. Check if you have python already by typing `python --version`. If the version is 3.6 or above then you can skip this section.
3. Go to www.python.org.
4. Go to 'Downloads' and click on any release 3.6 or higher to download it.
5. on windows or iOS, open your downloads folder and double-click the installer file. Follow the installer instructions. On ubuntu, python should be installed already; if it is not then something is _horribly_ wrong.
  
### B) How to install myokit
Full instructions for installing myokit on each operating system can be found here: www.myokit.org/install

### C) How to install git
Type `git --version` to check if you have git already.
- On windows, you can download an installer from  www.git-scm.com/download/win.
- On ubuntu, run `sudo apt-get install git`.
- On iOS, the command above will show you how to install it if it is not installed.

### D) How to install PKPD
1. Make sure you have python and myokit installed. ![install-pic](install-pic.png)
2. Open the terminal (or command line, on windows) and go to the folder you want to download to (using `cd`).
3. Download PKPD using:-
```
git clone https://github.com/SABS-R3-projects/PKPD/
```
4. Enter the installed directory by typing
```
cd PKPD
```
5. Install the PKPD module and all dependencies with
```
pip install -e .
```
Congratulations! You successfully installed PKPD.

### E) Use
Start the program by opening a terminal (or command line, on windows) and typing
```
python3 -m PKPD
```
### F) Troubleshooting
**I get the message `Command 'git' not found`**

You might not have git installed: go to that section. Alternatively, you can download a .zip file from github, unzip it, and proceed with the instructions in the same way from there.

**I get the message `'python' is not recognized as an internal or external command, operable program or batch file`**

Try replacing `python` with `python3`. If this doesn't work then you might not have python installed: go to that section.

**I get the message `Command 'pip' not found`**

Try replacing `pip` with `pip3`. If this doesn't work then you might not have python installed: go to that section.

**I get the message `ṫ̵̛͇̺͇͓͐̈́̀͒̿̏̆͝h̵̡̯̮̬̍͗̿̐̐̏̅͗̉̆̅̉͜ĕ̴͓̯͉͗̒̎͑͂̂̒̒͗̈́̓ṛ̶̡̭̗͕̀̄̅͐ę̶͔̹̥̖̠̼̎i̷̞̗̥̮̒̕s̵̲̱̭͔͙̑̐̾́̀̏̊̚͠â̶̧̫̣̗͔̘̹̝͓̬͇͒̿́̿̎ͅn̵̢̨̹̼̭̯͈̻̺̼̉̿̊̾͂̅͆͋̾̓͠ͅê̷̻͚̞̠̻̥̦͉̥͉̳̼̓͐̀́̓̌͗̃̕͠͝r̴̢̤͖̫͇̰̦̾͐̐̋͋͑̇͑͝r̸̛̛̼͔̺̹̯̼̻̅̾̐̅̋̋̉̍̀̚͝o̸͉̖̗̮̣͙͆̔̚r̵̠̳̖̟͉̞̰͕͍͂̋͒̾͗̿̋͜i̴̩̬͕̙̠͂̀̅n̴̢̢̳̤̥̣̠̻̹̥̼̮̞͑̍̒̈t̵̖̉̐̃́̊̌̋̚͝͝h̸̪̞͕̘̯̞͒̅̇e̴̠̓͌̒ṃ̷̧̭̞̬̳̹͔̹̙̈̊̑̓̇͛͒̓å̷͚̲̝͖̬̗̓͐̾̀̈͒͂̚͝ͅt̶͚̗͇̹̦̀͛̋ŗ̶̯͕̟̜͇̣̬̻̖̗̆̈́̍̊̀̎̈̑͑́͜͠i̸̡̡̛̟̺̮̤̽̒̋͒͝x̶̠̯͔̯̖̼̣̫͔̲̼̳̃̎`**

Your computer is haunted. Consider employing an exorcist.
