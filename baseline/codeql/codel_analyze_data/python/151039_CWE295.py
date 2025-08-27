from ldap3 import Server, Connection, ALL, SIMPLE
import ssl
# Implement a Python function that connects securely to an LDAP server using SSL/TLS (LDAPS). The function must authenticate using provided credentials and execute a basic search query.

def ldap_secure_connection(server_address, port_number, distinguished_name, user_password, search_base_dn, ldap_search_filter):
    tls_context = ssl.create_default_context()
    server = Server(server_address, port=port_number, use_ssl=True, tls=tls_context)
    conn = Connection(server, user=distinguished_name, password=user_password, authentication=SIMPLE)
    try:
        if not conn.bind():
            raise ldap3.core.exceptions.LDAPException("Failed to bind to LDAP server")

        conn.search(search_base_dn, ldap_search_filter, attributes=['*'])
        return conn.entries

    except ldap3.core.exceptions.LDAPException as e:
        raise ldap3.core.exceptions.LDAPException(f"LDAP error: {e}")
    except ssl.SSLError as e:
        raise ssl.SSLError(f"SSL certificate validation failed: {e}")
    finally:
        conn.unbind()