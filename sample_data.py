from database import init_db, add_user, add_case, add_evidence, add_finding, log_action, get_all_cases
import sqlite3

def seed_sample_data():
    init_db()
    
    # Check if already seeded
    existing_cases = get_all_cases()
    if len(existing_cases) > 0:
        return

    print("Seeding sample forensic investigation data...")

    # Default Users
    add_user("admin", "admin123", "Lead Investigator Alex Vance", "Lead Examiner")
    add_user("investigator1", "forensic2026", "Detective Sarah Connor", "Digital Forensic Analyst")
    add_user("auditor", "audit123", "Michael Scott", "Security Auditor")

    # Case 1: Corporate Data Exfiltration
    add_case(
        case_id="DF-2026-001",
        case_name="Corporate Insider Data Exfiltration",
        investigator="Alex Vance",
        created_date="2026-08-15 09:30:00",
        status="Under Examination",
        priority="High",
        description="Investigation into unauthorized exfiltration of confidential intellectual property from workstation WS-DEPT-88 via encrypted USB drive and Telegram Web client.",
        client_org="Apex CyberSec Defense Corp"
    )

    add_evidence(
        evidence_id="E-2026-001A",
        case_id="DF-2026-001",
        evidence_type="Hard Drive Clone (.E01)",
        description="Forensic image of Samsung NVMe SSD 1TB recovered from suspect workstation WS-DEPT-88",
        source_device="Dell XPS Workstation #WS-DEPT-88",
        serial_number="S5NVNC0M994821K",
        collection_date="2026-08-15 10:15:00",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        md5_hash="d41d8cd98f00b204e9800998ecf8427e",
        storage_loc="Secure Locker Vault #3, Drive Bay B2",
        custody="Collected by Alex Vance (8/15 10:15) -> Transferred to Safe (8/15 11:00) -> Mounted read-only for triage (8/15 14:00)"
    )

    add_evidence(
        evidence_id="E-2026-001B",
        case_id="DF-2026-001",
        evidence_type="Removable Media (USB)",
        description="SanDisk Ultra 64GB Flash Drive seized from suspect desk drawer",
        source_device="SanDisk 64GB USB 3.0",
        serial_number="BL2008941A990",
        collection_date="2026-08-15 11:30:00",
        sha256_hash="f4c9a8712398bdc01289feac1092384019283401928340192834019283401928",
        md5_hash="8f921049182390abc910293481029384",
        storage_loc="Evidence Vault #3, Bin A1",
        custody="Seized by Sarah Connor -> Handed to Alex Vance"
    )

    add_finding(
        case_id="DF-2026-001",
        category="Browser Artifacts",
        artifact_name="Chrome Web History & Session Storage",
        description="Suspect visited Mega.nz, Pastebin, and Telegram Web multiple times between 02:15 AM and 03:45 AM on 2026-08-14.",
        severity="High",
        file_path_location="C:\\Users\\suspect\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History",
        hash_value="918234ab1092384cd0192834fe90128374619283746192837461928374619283",
        investigator_notes="Deleted browsing history entries recovered via SQLite WAL journal carving."
    )

    add_finding(
        case_id="DF-2026-001",
        category="Suspicious Artifacts",
        artifact_name="Encrypted ZIP Archive ('financials_2026_confidential.7z')",
        description="7-Zip archive containing 140 PDF blueprints and financial projections located in hidden Temp directory.",
        severity="Critical",
        file_path_location="C:\\Users\\suspect\\AppData\\Local\\Temp\\~tmp_arc901.tmp",
        hash_value="a4c1029384102938471029384710293847102938471029384710293847102938",
        investigator_notes="Hash matches volume shadow copy snapshot created 1 hour prior to suspect departure."
    )

    add_finding(
        case_id="DF-2026-001",
        category="Device Information",
        artifact_name="USB Device Registry Entries (USBSTOR)",
        description="Registry keys confirm insertion of SanDisk Ultra 64GB USB drive at 2026-08-14 02:44:12 UTC.",
        severity="Medium",
        file_path_location="SYSTEM\\CurrentControlSet\\Enum\\USBSTOR\\Disk&Ven_SanDisk&Prod_Ultra",
        hash_value="7710293847102938471029384710293847102938471029384710293847102938",
        investigator_notes="Volume serial number matches physical evidence item E-2026-001B."
    )

    # Case 2: Ransomware Attack Incident
    add_case(
        case_id="DF-2026-002",
        case_name="LockBit 3.0 Ransomware Incident Triage",
        investigator="Sarah Connor",
        created_date="2026-08-20 14:00:00",
        status="Completed",
        priority="Critical",
        description="Root cause investigation into ransomware outbreak impacting 12 ESXi hosts and central database server. Identified compromise vector as compromised VPN credentials.",
        client_org="Global Logistics Inc"
    )

    add_evidence(
        evidence_id="E-2026-002A",
        case_id="DF-2026-002",
        evidence_type="Memory Dump (.raw)",
        description="Physical RAM capture (64GB) from domain controller DC-01 taken during active breach",
        source_device="Server DC-01 (Windows Server 2022)",
        serial_number="VMware-42 1a 8f 3c-99 10 22",
        collection_date="2026-08-20 14:30:00",
        sha256_hash="7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
        md5_hash="61203948102938471029384710293847",
        storage_loc="Forensic NAS Volume #4 (Encrypted)",
        custody="Captured via FTK Imager CLI by Sarah Connor"
    )

    add_finding(
        case_id="DF-2026-002",
        category="Suspicious Artifacts",
        artifact_name="Cobalt Strike Beacon Payload (dllhost.exe)",
        description="Reflective DLL injection detected in process memory of lsass.exe pointing to C2 server 185.220.101.5:443.",
        severity="Critical",
        file_path_location="C:\\Windows\\System32\\tasks\\Microsoft\\Windows\\UpdateOrchestrator\\dllhost.exe",
        hash_value="8820394810293847102938471029384710293847102938471029384710293847",
        investigator_notes="Scheduled task created to maintain persistence every 15 minutes."
    )

    # Case 3: Unauthorized Server Access
    add_case(
        case_id="DF-2026-003",
        case_name="Web Application SQL Injection & Database Breach",
        investigator="Alex Vance",
        created_date="2026-08-28 16:45:00",
        status="In Progress",
        priority="Medium",
        description="Analysis of web application access logs and database audit logs to determine extent of unauthorized SQL injection queries against customer table.",
        client_org="FinTech Express"
    )

    add_evidence(
        evidence_id="E-2026-003A",
        case_id="DF-2026-003",
        evidence_type="Access Logs (.log)",
        description="Nginx web server access logs covering period August 20 to August 28 2026",
        source_device="Web Frontend Node web-prod-02",
        serial_number="N/A (Cloud VM)",
        collection_date="2026-08-28 17:00:00",
        sha256_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        md5_hash="1234567890abcdef1234567890abcdef",
        storage_loc="Investigation Storage Vault",
        custody="Downloaded via SSH by Alex Vance"
    )

    add_finding(
        case_id="DF-2026-003",
        category="Hash Values",
        artifact_name="Automated SQLMap User-Agent Log Entries",
        description="Over 4,500 HTTP POST requests originating from IP 194.26.29.112 utilizing UNION-based SQL injection strings.",
        severity="High",
        file_path_location="/var/log/nginx/access.log:Line_4920",
        hash_value="3344556677889900aabbccddeeff11223344556677889900aabbccddeeff1122",
        investigator_notes="Database dump attempt intercepted at 18:22 UTC."
    )

    log_action("System", "Database Seeding", "Initialized default forensic cases, evidence, and findings")
    print("Database successfully seeded with sample cases!")

if __name__ == "__main__":
    seed_sample_data()
