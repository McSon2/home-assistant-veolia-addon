#!/usr/bin/with-contenv bashio

# Retrieve add-on configuration
email=$(bashio::config 'email')
password=$(bashio::config 'password')
abo_id=$(bashio::config 'abo_id')
token=$(bashio::config 'token')

# Execute the Python script with the provided configuration
exec python3 /veolia_client.py --email "$email" --password "$password" --abo_id "$abo_id" --token "$token"
