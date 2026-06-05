"""MongoDB Atlas connection diagnostic script.

This script performs read-only diagnostics:
1. Load environment variables from .env
2. Validate MONGODB_URL is present
3. Connect with PyMongo
4. Execute client.admin.command("ping")
5. List databases
6. List collections from biologics_platform
7. Print full exception stack trace on failure
8. Check whether dnspython is installed
9. Check whether Atlas DNS SRV resolution works
10. Report the likely root cause and recommended fix
"""

import os
import sys
import traceback
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
except ImportError:
    print("ERROR: PyMongo is not installed. Install with: pip install pymongo")
    sys.exit(1)

try:
    import dns.resolver
    DNSPYTHON_AVAILABLE = True
except ImportError:
    DNSPYTHON_AVAILABLE = False


def print_heading(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def parse_mongodb_host(uri):
    parsed = urlparse(uri)
    if parsed.scheme.startswith("mongodb"):
        return parsed.hostname
    return None


def resolve_srv(hostname):
    try:
        answers = dns.resolver.resolve(hostname, "SRV")
        return [str(rdata) for rdata in answers]
    except Exception as exc:
        raise


def configure_custom_dns(servers):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = servers
        dns.resolver.default_resolver = resolver
        print(f"Using custom DNS servers: {servers}")
    except Exception:
        print("WARNING: Unable to configure custom DNS servers.")
        traceback.print_exc()


def main():
    print_heading("MongoDB Atlas Diagnostic")

    if load_dotenv is not None:
        load_dotenv()
        print("Loaded environment from .env (if present)")
    else:
        print("python-dotenv is not installed; using environment variables only")

    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "biologics_platform")

    print(f"MONGODB_URL present: {bool(mongodb_url)}")
    if mongodb_url:
        print(f"MONGODB_URL: {mongodb_url}")
    else:
        print("ERROR: MONGODB_URL environment variable is not set.")
        print("Create a .env file or export MONGODB_URL with your Atlas connection string.")
        sys.exit(1)

    mongodb_dns_servers = [s.strip() for s in os.getenv("MONGODB_DNS_SERVERS", "").split(",") if s.strip()]
    print(f"DATABASE_NAME: {database_name}")
    print(f"PyMongo version: {__import__('pymongo').__version__}")
    print(f"dnspython installed: {DNSPYTHON_AVAILABLE}")
    print(f"MONGODB_DNS_SERVERS: {mongodb_dns_servers}")

    if mongodb_url.startswith("mongodb+srv://"):
        host = parse_mongodb_host(mongodb_url)
        print(f"Parsed SRV hostname: {host}")
        if host is None:
            print("ERROR: Could not parse hostname from MONGODB_URL.")
        elif not DNSPYTHON_AVAILABLE:
            print("WARNING: dnspython is required for mongodb+srv URIs.")
            print("Install it with: pip install dnspython")
        else:
            if mongodb_dns_servers:
                configure_custom_dns(mongodb_dns_servers)
            print_heading("DNS SRV Resolution")
            try:
                records = resolve_srv(host)
                print(f"SRV records for {host}:")
                for record in records:
                    print(f"  - {record}")
            except Exception:
                print("ERROR: Atlas DNS SRV resolution failed.")
                traceback.print_exc()
                print("This usually means DNS resolution is blocked, dnspython is missing, or the host name is invalid.")
                print("Check your network and DNS settings, and ensure the SRV host is reachable.")

    print_heading("Attempting MongoDB Connection")
    client = None
    try:
        client = MongoClient(
            mongodb_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=False,
        )

        print("Sending ping to MongoDB server...")
        ping_result = client.admin.command("ping")
        print(f"Ping response: {ping_result}")

        print_heading("List Databases")
        db_names = client.list_database_names()
        print(f"Databases ({len(db_names)}): {db_names}")

        print_heading(f"List Collections in {database_name}")
        if database_name in db_names:
            db = client[database_name]
            try:
                collections = db.list_collection_names()
                print(f"Collections ({len(collections)}): {collections}")
            except Exception as inner_exc:
                print(f"ERROR: Failed to list collections in {database_name}: {inner_exc}")
                traceback.print_exc()
        else:
            print(f"Database '{database_name}' not found in the server list.")

        print_heading("Diagnosis Summary")
        print("MongoDB connection succeeded. Atlas DNS SRV resolution is working if using mongodb+srv.")
        print("The server is reachable and read-only diagnostics completed successfully.")
    except Exception as exc:
        print("\nERROR: Unable to connect to MongoDB Atlas.")
        traceback.print_exc()

        root_cause = "Unknown"
        message = str(exc).lower()

        if isinstance(exc, ConfigurationError):
            if "resolution lifetime expired" in message or "dns" in message or "srv" in message:
                root_cause = "Atlas DNS SRV resolution timed out."
            else:
                root_cause = "Invalid MongoDB URI or client configuration."
        elif isinstance(exc, ServerSelectionTimeoutError) or isinstance(exc, ConnectionFailure):
            if "resolution lifetime expired" in message or "dns" in message or "srv" in message or "getaddrinfo" in message:
                root_cause = "Atlas DNS SRV resolution failure."
            elif "winerror 10061" in message or "connection refused" in message:
                root_cause = "Connection refused. The target host rejected the connection."
            elif "authentication failed" in message or "auth" in message:
                root_cause = "Authentication failure. Check your username/password and database credentials."
            else:
                root_cause = "Server selection or network issue."
        elif not DNSPYTHON_AVAILABLE and mongodb_url.startswith("mongodb+srv://"):
            root_cause = "dnspython is not installed for mongodb+srv URI resolution."

        print_heading("Root Cause Analysis")
        print(f"Root cause: {root_cause}")
        if mongodb_url.startswith("mongodb+srv://") and not DNSPYTHON_AVAILABLE:
            print("Fix: Install dnspython with: pip install dnspython")
        elif mongodb_url.startswith("mongodb+srv://") and DNSPYTHON_AVAILABLE:
            print("Fix: Atlas DNS SRV lookup is failing. Check network/DNS or use a different DNS server.")
            print("       Confirm that your machine can resolve the SRV host and allow outbound DNS queries.")
        elif mongodb_url.startswith("mongodb://localhost"):
            print("Fix: If you intended to connect locally, start MongoDB on localhost:27017 or update MONGODB_URL.")
        else:
            print("Fix: Verify the MongoDB URI, network access, Atlas IP whitelist, and credentials.")

        sys.exit(1)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
