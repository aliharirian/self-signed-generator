from OpenSSL import crypto
from jinja2 import Template
import os
import yaml


def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def read_config(config_file):
    with open(config_file, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def generate_ca(cert_path, key_path, country, state, locality):
    # Check if CA files already exist
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("CA files already exist. Skipping CA generation.")
        return

    # Create root CA & Private key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()
    cert.get_subject().C = country
    cert.get_subject().ST = state
    cert.get_subject().L = locality
    cert.set_serial_number(1)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(7500 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(key_path, 'wb') as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    with open(cert_path, 'wb') as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))


def generate_certificate(domain, certs_dir, ca_key_path, ca_cert_path):
    # Generate Private key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create X.509 request
    req = crypto.X509Req()
    req.get_subject().CN = domain
    req.set_pubkey(key)
    req.sign(key, 'sha256')

    with open(os.path.join(certs_dir, f'{domain}.key'), 'wb') as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # Load the Jinja2 template from csr_template.conf.j2
    with open('templates/csr_template.conf.j2', 'r') as template_file:
        template_content = template_file.read()

    template = Template(template_content)

    # Render the template with the provided values
    rendered_csr_conf = template.render(
        COUNTRY=country,
        STATE=state,
        LOCALITY=locality,
        DOMAIN=domain,
    )

    # Create csr.conf using the rendered template
    with open(os.path.join(certs_dir, 'csr.conf'), 'w') as csr_conf_file:
        csr_conf_file.write(rendered_csr_conf)

    # Load CA key and cert
    with open(ca_key_path, 'rb') as ca_key_file:
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_key_file.read())

    with open(ca_cert_path, 'rb') as ca_cert_file:
        ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())

    # Create SSL certificate signed by CA
    cert = crypto.X509()
    cert.get_subject().CN = domain
    cert.set_serial_number(2)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(7500 * 24 * 60 * 60)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(ca_key, 'sha256')

    with open(os.path.join(certs_dir, f'{domain}.crt'), 'wb') as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))


def generate_client_certificate(client_name, certs_dir, ca_key_path, ca_cert_path):
    # Generate Private key for the client
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a X.509 request for the client
    req = crypto.X509Req()
    req.get_subject().CN = client_name
    req.set_pubkey(key)
    req.sign(key, 'sha256')

    # Save the client's private key
    with open(os.path.join(certs_dir, f'{client_name}.key'), 'wb') as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # Load the CA's private key and certificate
    with open(ca_key_path, 'rb') as ca_key_file:
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_key_file.read())
    with open(ca_cert_path, 'rb') as ca_cert_file:
        ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())

    # Create a client certificate signed by the CA
    cert = crypto.X509()
    cert.get_subject().CN = client_name
    cert.set_serial_number(3)  # Ensure unique serial number
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(7500 * 24 * 60 * 60)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(ca_key, 'sha256')

    # Save the client's certificate
    with open(os.path.join(certs_dir, f'{client_name}.crt'), 'wb') as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    print(f"Client certificate for {client_name} generated successfully.")


if __name__ == "__main__":
    config = read_config('config.yml')

    domain = config.get('domain', "test.co")

    country = config.get('country', "IR")
    state = config.get('state', "Tehran")
    locality = config.get('locality', "Tehran")

    certs_dir = config.get('certs_dir', "certs")
    ca_file_name = config.get('ca_file_name', "root-ca")
    clients = config.get('clients')

    ensure_directory(certs_dir)

    if os.path.exists(f'{certs_dir}/{ca_file_name}.key') and os.path.exists(f'{certs_dir}/{ca_file_name}.crt'):
        ca_key_path = os.path.join(certs_dir, f'{ca_file_name}.key')
        ca_cert_path = os.path.join(certs_dir, f'{ca_file_name}.crt')
    else:
        ca_key_path = f'{certs_dir}/{ca_file_name}.key'
        ca_cert_path = f'{certs_dir}/{ca_file_name}.crt'

    generate_ca(ca_cert_path, ca_key_path, country, state, locality)
    generate_certificate(domain, certs_dir, ca_key_path, ca_cert_path)
    for client in clients:
        generate_client_certificate(client, certs_dir, ca_key_path, ca_cert_path)
