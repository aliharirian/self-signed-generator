# Self-Signed Generator

## Overview
The Self-Signed Generator is a Python-based tool designed to automate the creation of self-signed certificates. It simplifies the process of generating certificates for development environments or any situation where trusted certificates from a Certificate Authority (CA) are not required.

## Features
- **Easy Configuration**: Customize certificate properties via `config.yml`.
- **Template-based Generation**: Utilize customizable templates for generating certificates.
- **Simple CLI Interface**: Generate certificates with a simple command.

## Prerequisites
Before you begin, ensure you have the following installed on your system:
- Python 3.x
- pip (Python package manager)

## Installation

1. Clone the repository or download the ZIP file and extract it.
2. Navigate to the project directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Edit `config.yml` to specify the certificate properties such as validity, issuer, subject, and other relevant settings.

## Usage
To generate a self-signed certificate, run:
```bash
python main.py
```
Follow any on-screen prompts to customize your certificate generation process.

## Templates
The `templates` directory contains templates used for generating certificates. Modify these templates as needed to fit your requirements.

## Contributing
Contributions to the Self-Signed Generator are welcome. Please feel free to fork the repository, make changes, and submit pull requests.

## License
This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.
