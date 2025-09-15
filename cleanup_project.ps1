# ==============================================================================
# Script de Limpeza e Reorganização do Projeto Agent_BI
#
# Propósito: Isolar as ferramentas de desenvolvimento e manutenção na pasta 'dev_tools',
# conforme a nova arquitetura alvo, para limpar a raiz do projeto.
# ==============================================================================

# Define a cor do texto para as mensagens de status
$InfoColor = "Cyan"
$SuccessColor = "Green"
$WarningColor = "Yellow"

Write-Host "Iniciando a limpeza e reorganização do projeto Agent_BI..." -ForegroundColor $InfoColor
Write-Host "----------------------------------------------------"

# --- Passo 1: Criar o diretório dev_tools ---
$devToolsPath = ".\dev_tools"
if (-not (Test-Path $devToolsPath)) {
    Write-Host "A criar o diretório '$devToolsPath'..." -ForegroundColor $InfoColor
    New-Item -ItemType Directory -Path $devToolsPath
    Write-Host "Diretório '$devToolsPath' criado com sucesso." -ForegroundColor $SuccessColor
} else {
    Write-Host "O diretório '$devToolsPath' já existe." -ForegroundColor $WarningColor
}

# --- Passo 2: Mover os diretórios de suporte ---
# Lista de diretórios a serem movidos
$foldersToMove = @("scripts", "dags", "tools")

foreach ($folder in $foldersToMove) {
    $sourcePath = ".\$folder"
    $destinationPath = "$devToolsPath\$folder"

    # Verifica se a pasta de origem existe antes de tentar movê-la
    if (Test-Path $sourcePath) {
        Write-Host "A mover '$sourcePath' para '$destinationPath'..." -ForegroundColor $InfoColor
        Move-Item -Path $sourcePath -Destination $devToolsPath
        Write-Host "Diretório '$folder' movido com sucesso." -ForegroundColor $SuccessColor
    } else {
        Write-Host "O diretório '$sourcePath' não foi encontrado. A ignorar." -ForegroundColor $WarningColor
    }
}

Write-Host "----------------------------------------------------"
Write-Host "Limpeza e reorganização concluídas com sucesso!" -ForegroundColor $SuccessColor