#!/bin/sh

sudo cat files.txt | xargs rm -rf
sudo rm -rf ~/.nglib
sudo rm files.txt

