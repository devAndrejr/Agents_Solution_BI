# Caminhos
$venvPath = "U:\Meu Drive\Caçula\Langchain\Agent_BI\.venv\Lib\site-packages"
$venvScripts = "U:\Meu Drive\Caçula\Langchain\Agent_BI\.venv\Scripts"

Write-Host "==== Limpando dist-info antigos/corrompidos ===="
$distInfos = Get-ChildItem -Path $venvPath -Filter "*.dist-info" -Directory -ErrorAction SilentlyContinue
foreach ($folder in $distInfos) { Remove-Item -Recurse -Force $folder.FullName }

Write-Host "==== Ativando venv ===="
& (Join-Path $venvScripts "Activate.ps1")

Write-Host "==== Reinstalando pacotes essenciais ===="
pip install --upgrade --force-reinstall pip setuptools wheel huggingface_hub

Write-Host "==== Instalando dependências para análise em Python ===="
pip install --upgrade --force-reinstall networkx plotly pandas
