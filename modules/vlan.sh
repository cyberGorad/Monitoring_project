#!/bin/bash

# Adresse de base à tester (ex: 192.168.X.0/24)
BASE="192.168"
RANGE_START=1
RANGE_END=254
IP_PER_NET=254

echo "📡 Scan de réseaux voisins : $BASE.[${RANGE_START}-${RANGE_END}].0/24"

for NET in $(seq $RANGE_START $RANGE_END); do
    echo "🔎 Scanning réseau $BASE.$NET.0/24"

    for HOST in $(seq 1 $IP_PER_NET); do
        TARGET="$BASE.$NET.$HOST"
        (ping -c 1 -W 1 $TARGET > /dev/null 2>&1 && echo "✅ $TARGET est joignable") &
    done

    wait
    echo "➡️ Fin du scan $BASE.$NET.0/24"
    echo "---------------------------------------"
done

echo "✅ Scan complet terminé."
