import os
import jpype
import jaydebeapi
import logging
from contextlib import contextmanager

# Configure logging for troubleshooting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration (matching your DBeaver setup)
PG_JAR = r"I:\configs\dbeaver\postgresql-42.3.3.jar"
KRB5_CONF = r"I:\configs\dbeaver\krb5.conf"
JAAS_CONF = r"I:\configs\dbeaver\jaas.conf"
HOST = "P001-104990-104991.na.cockroachdb.jpmchase.net"
PORT = 26300
DB = "defaultdb"
SPN = "cockroachdb"

def ensure_kerberos_ticket() -> bool:
    """Quick check that Kerberos ticket exists"""
    ticket_cache = r"C:\Users\N123456\krb5cc_N123456"
    if not os.path.exists(ticket_cache):
        logger.warning(f"Kerberos ticket cache not found at {ticket_cache}")
        logger.warning("Run 'kinit' to authenticate")
        return False
    return True

def get_connection() :
    """Get a CockroachDB connection via JDBC with Kerberos"""
    
    # Verify ticket before attempting connection
    if not ensure_kerberos_ticket():
        raise Exception("No valid Kerberos ticket found")
    
    # Start JVM only once per process
    if not jpype.isJVMStarted():
        logger.info("Starting JVM with Kerberos configuration")
        jpype.startJVM(
            jpype.getDefaultJVMPath(),
            f"-Djava.class.path={PG_JAR}",
            f"-Djava.security.krb5.conf={KRB5_CONF}",
            f"-Djava.security.auth.login.config={JAAS_CONF}",
            "-Djavax.security.auth.useSubjectCredsOnly=false",
            "-Duser.timezone=UTC",  # Added to match DBeaver config
            # Uncomment for debugging:
            # "-Dsun.security.krb5.debug=true",
            # "-Djava.net.debug=gss,handshake,ssl",
        )
    
    # JDBC URL with all necessary parameters
    jdbc_url = (
        f"jdbc:postgresql://{HOST}:{PORT}/{DB}"
        "?sslmode=require"
        f"&kerberosServerName={SPN}"
        "&gssEncMode=disable"
        "&connectTimeout=20"
        "&socketTimeout=300"  # 5 min timeout for long queries
    )
    
    # Properties (jaasApplicationName must match your JAAS stanza)
    props = {
        "jaasApplicationName": "pgjdbc",  # Must match JAAS config
        "ApplicationName": "Python-JDBC-Kerberos",  # For tracking in DB
    }
    
    logger.info(f"Connecting to {HOST}:{PORT}/{DB}")
    return jaydebeapi.connect("org.postgresql.Driver", jdbc_url, props, PG_JAR)

@contextmanager
def cockroach_connection():
    """Context manager for safe connection handling"""
    conn = None
    try:
        conn = get_connection()
        logger.info("Connection established successfully")
        yield conn
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Connection closed")

# Example usage for your reconciliation queries
def run_reconciliation_query(query, params=None):
    """Execute a query for production issue research"""
    with cockroach_connection() as conn:
        cur = conn.cursor()
        
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        # Fetch all results
        results = cur.fetchall()
        
        # Get column names for better output
        columns = [desc[0] for desc in cur.description]
        
        cur.close()
        
        return columns, results

# Test the connection
if __name__ == "__main__":
    try:
        # Simple connection test
        with cockroach_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT current_user, version()")
            user, version = cur.fetchone()
            print(f"✓ Connected as: {user}")
            print(f"✓ Database version: {version[:50]}...")  # First 50 chars
            cur.close()
        
        # Example reconciliation query
        columns, results = run_reconciliation_query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5"
        )
        
        print(f"\nTables in public schema:")
        for row in results:
            print(f"  - {row[0]}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()