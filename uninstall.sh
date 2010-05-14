#!/bin/sh

cat files.txt | xargs sudo rm -rf
sudo rm -rf ~/.nglib
sudo rm files.txt

