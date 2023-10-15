#!/bin/bash

openssl genrsa -out private.key 2048
openssl req -new -key private.key -out cert.csr
openssl x509 -req -days 365 -in cert.csr -signkey private.key -out certificate.crt
rm cert.csr

mv private.key certificate.crt $HOME/.local/share/SecureDataTransfer/certs