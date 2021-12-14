#!/usr/bin/env bash
:<<'EOF'
cron: 30 9 * * *
new Env('debuenv');
EOF
printenv
echo $kois
