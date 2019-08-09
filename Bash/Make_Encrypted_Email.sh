#!/bin/bash

echo Output File Name?
read outputfilename

echo Recipient\'s E-Mail Address?
read recipient

echo Data or File to be Signed and Encrypted?
read mypublickey

gpg -a -o "$outputfilename" -r "$recipient" -se "$mypublickey"
