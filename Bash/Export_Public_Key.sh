#!/bin/bash

echo Output file name?  
read outputfilename

echo Key Fingerprint?
read keyprint

gpg -a -o "$outputfilename" --export "$keyprint"

