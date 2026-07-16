#!/bin/bash
# 🐕 GUARDA DE CITAÇÃO — duplo-clique
# Verifica que as regras citadas (<<CITA ID>> … <<FIM>>) nos .md desta pasta
# são, letra a letra, as palavras do Vasco na REGRAS_DO_VASCO.md.
cd "$(dirname "$0")"
echo
python3 guarda_citacao.py "$@"
codigo=$?
echo
if [ $codigo -ne 0 ]; then
  echo "🚨 O GUARDA DISPAROU (código $codigo). Há citações fora da fonte — corrige antes de seguir."
else
  echo "✅ Guarda passou."
fi
echo
echo "Podes fechar esta janela."
