#!/bin/bash

# Set CodeQL version and download URL
CODEQL_VERSION="2.20.6"
CODEQL_ZIP="codeql-linux64.zip"
CODEQL_URL="https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/${CODEQL_ZIP}"
CODEQL_HOME="$HOME/codeql-home"

# Download CodeQL
echo "Downloading CodeQL..."
curl -L "$CODEQL_URL" -o "$CODEQL_ZIP"

# Create CodeQL home directory
echo "Creating CodeQL home directory at $CODEQL_HOME..."
mkdir -p "$CODEQL_HOME"

# Unzip CodeQL
echo "Unzipping CodeQL to $CODEQL_HOME..."
unzip "$CODEQL_ZIP" -d "$CODEQL_HOME" && rm "$CODEQL_ZIP"

# Clone the CodeQL query repository
echo "Cloning CodeQL query repository..."
cd "$CODEQL_HOME"
git clone --recursive https://github.com/github/codeql.git codeql-repo

# Add CodeQL directory to PATH
echo "Adding CodeQL to PATH..."
export PATH="$PATH:$CODEQL_HOME/codeql"

# Ensure PATH settings persist
echo 'export PATH="$PATH:$HOME/codeql-home/codeql"' >> ~/.bashrc

# Check CodeQL configuration
echo "Checking CodeQL configuration..."
codeql resolve languages
codeql resolve qlpacks

echo "CodeQL installation completed successfully!"
