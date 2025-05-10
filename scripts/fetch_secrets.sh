#!/bin/bash

# Check if required arguments are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <VAULT_NAME> <OUTPUT_FILE> [AT_OUTPUT_FILE]"
    exit 1
fi

# Variables
VAULT_NAME=$1
OUTPUT_FILE=$2
AT_OUTPUT_FILE=${3:-at.env}  # Default to "at.env" if not provided

# Clear the output files
> "$OUTPUT_FILE"
> "$AT_OUTPUT_FILE"

# Keys list for At env file
at_env_keys=("BASE_URL" "EMAIL" "PASSWORD" "AZURE_ACCOUNT_NAME" "AZURE_ACCOUNT_KEY" "AZURE_CONTAINER")

# Retrieve all secrets
secrets=$(az keyvault secret list --vault-name "$VAULT_NAME" --query "[].id" -o tsv)

# Loop through each secret and retrieve its value
for secret_id in $secrets; do
    secret_name=$(basename "$secret_id")
    secret_value=$(az keyvault secret show --id "$secret_id" --query "value" -o tsv)
    
    # Replace '---' with '_' in the secret name
    formatted_secret_name=$(echo "$secret_name" | sed 's/---/_/g')

    # Check if the secret name is in the at_env_keys array
    if [[ " ${at_env_keys[@]} " =~ " ${formatted_secret_name} " ]]; then
        echo "$formatted_secret_name=$secret_value" >> "$AT_OUTPUT_FILE"
    fi
    
    # Write to the main .env file in KEY=VALUE format
    echo "$formatted_secret_name=$secret_value" >> "$OUTPUT_FILE"
done

echo "Secrets written to $OUTPUT_FILE"
echo "At environment secrets written to $AT_OUTPUT_FILE"
