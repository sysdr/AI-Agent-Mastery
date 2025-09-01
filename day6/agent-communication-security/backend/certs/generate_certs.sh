#!/bin/bash
# Generate CA
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem -subj "/C=US/ST=CA/L=SF/O=AgentSec/CN=ca"

# Generate server cert
openssl genrsa -out server-key.pem 4096
openssl req -subj "/C=US/ST=CA/L=SF/O=AgentSec/CN=localhost" -sha256 -new -key server-key.pem -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.pem -CAkey ca-key.pem -out server-cert.pem -sha256

# Generate client cert
openssl genrsa -out client-key.pem 4096
openssl req -subj "/C=US/ST=CA/L=SF/O=AgentSec/CN=client" -new -key client-key.pem -out client.csr
openssl x509 -req -days 365 -in client.csr -CA ca.pem -CAkey ca-key.pem -out client-cert.pem -sha256

rm server.csr client.csr
chmod 400 *-key.pem
chmod 444 *.pem
