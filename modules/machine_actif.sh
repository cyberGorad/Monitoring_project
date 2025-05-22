#!/bin/bash

# Détection automatique de l'IP locale et du sous-réseau
IP_LOCAL=$(ip route get 1 | awk '{print $7; exit}')
RESEAU=$(echo $IP_LOCAL | cut -d"." -f1-3) # Exemple : 192.168.1

echo "📡 Scan des machines joignables sur le réseau $RESEAU.0/24..."
echo "------------------------------------------------------------"

for i in {1..254}; do
    IP="$RESEAU.$i"
    (ping -c 1 -W 1 $IP > /dev/null 2>&1 && echo "✅ Machine joignable : $IP") &
done

wait
echo "------------------------------------------------------------"
echo "✅ Scan terminé."
