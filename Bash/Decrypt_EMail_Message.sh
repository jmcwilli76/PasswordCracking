#!/bin/bash

echo Encrypted Message File Name?
read inputfile

echo Decrypted Message Output File Name?
read outputfile

gpg -o "$outputfile" -d "$inputfile"
