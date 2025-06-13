#!/bin/bash

echo "Закрываю все процессы Node.js и Python..."

# Закрыть все процессы node
pkill node

# Закрыть все процессы python (в том числе python3)
pkill -f python

echo "Все процессы Node.js и Python завершены."
