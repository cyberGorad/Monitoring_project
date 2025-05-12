import subprocess
import re

def get_active_ssh_sessions():
    try:
        # Liste les connexions SSH (port 22 en écoute) établies
        result = subprocess.check_output(['ss', '-tnp'], universal_newlines=True)

        print("🔐 Connexions SSH actives détectées :\n")
        for line in result.splitlines():
            if ':22' in line and 'ESTAB' in line and 'sshd' in line:
                # Exemple : ESTAB 0 0 192.168.1.10:ssh 192.168.1.5:53344 users:(("sshd",pid=1234,fd=3))
                match = re.search(r'(\d+\.\d+\.\d+\.\d+):\d+.*users:\(\("sshd",pid=(\d+)', line)
                if match:
                    ip = match.group(1)
                    pid = match.group(2)

                    # Trouver l'utilisateur associé à ce PID
                    user = subprocess.check_output(['ps', '-o', 'user=', '-p', pid], universal_newlines=True).strip()
                    print(f"➡️  Utilisateur : {user} | IP : {ip} | PID : {pid}")

    except subprocess.CalledProcessError as e:
        print("Erreur lors de l’analyse des connexions SSH :", e)

get_active_ssh_sessions()
