Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$texDir = Split-Path -Parent $scriptDir
$docsDir = Split-Path -Parent $texDir
$sourceFile = Join-Path $docsDir "MANUAL_USUARIO_GLOBAL_INSTALACIONES.tex"

function Get-BlockByRegex {
    param(
        [string]$Text,
        [string]$StartPattern,
        [string]$EndPattern
    )

    $pattern = "(?s)$StartPattern.*?(?=$EndPattern)"
    $match = [regex]::Match($Text, $pattern)

    if (-not $match.Success) {
        throw "No se pudo extraer el bloque entre '$StartPattern' y '$EndPattern'."
    }

    return $match.Value.Trim() + "`r`n"
}

function Write-Utf8File {
    param(
        [string]$Path,
        [string]$Content
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

if (-not (Test-Path -LiteralPath $sourceFile)) {
    throw "No existe el archivo origen: $sourceFile"
}

$sourceText = Get-Content -LiteralPath $sourceFile -Raw -Encoding UTF8

$globalCommon = Get-BlockByRegex `
    -Text $sourceText `
    -StartPattern "\\section\{Finalidad del manual\}" `
    -EndPattern "\\section\{Particularidades de cada instalaci.n\}"

$aguaSection = Get-BlockByRegex `
    -Text $sourceText `
    -StartPattern "\\section\{Instalaci.n de Agua\}" `
    -EndPattern "\\section\{Instalaci.n de Saneamiento\}"

$saneamientoSection = Get-BlockByRegex `
    -Text $sourceText `
    -StartPattern "\\section\{Instalaci.n de Saneamiento\}" `
    -EndPattern "\\section\{Instalaci.n de Ventilaci.n\}"

$ventilacionSection = Get-BlockByRegex `
    -Text $sourceText `
    -StartPattern "\\section\{Instalaci.n de Ventilaci.n\}" `
    -EndPattern "\\section\{Instalaci.n de Electricidad\}"

$electricidadSection = Get-BlockByRegex `
    -Text $sourceText `
    -StartPattern "\\section\{Instalaci.n de Electricidad\}" `
    -EndPattern "\\section\{Pr.ximas unidades por instalaci.n\}"

$proximasUnidades = Get-BlockByRegex `
    -Text $sourceText `
    -StartPattern "\\section\{Pr.ximas unidades por instalaci.n\}" `
    -EndPattern "\\end\{document\}"

$commonDir = Join-Path $texDir "comun"
$sectionsDir = Join-Path $texDir "secciones"

$preamble = @'
\usepackage[spanish,es-tabla]{babel}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{setspace}
\usepackage{parskip}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{float}
\usepackage{enumitem}
\usepackage{xcolor}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    pdftitle={Manual de Usuario Global de Instalaciones},
    pdfauthor={OpenAI Codex}
}

\setstretch{1.1}
\setlist[itemize]{topsep=4pt,itemsep=2pt}
\setlist[enumerate]{topsep=4pt,itemsep=2pt}
\graphicspath{{../}}

\newcommand{\placeholderimage}[2]{
    \begin{figure}[H]
        \centering
        \fbox{\parbox[c][6cm][c]{0.88\textwidth}{
            \centering
            \textbf{#1}\\[0.4cm]
            #2
        }}
        \caption{#2}
    \end{figure}
}

\newcommand{\manualimage}[2]{
    \IfFileExists{#1}{
        \begin{figure}[H]
            \centering
            \includegraphics[width=0.9\textwidth]{#1}
            \caption{#2}
        \end{figure}
    }{
        \placeholderimage{#1}{#2}
    }
}

\newcommand{\manualimagesized}[4]{
    \IfFileExists{#1}{
        \begin{figure}[H]
            \centering
            \includegraphics[width=#3,height=#4,keepaspectratio]{#1}
            \caption{#2}
        \end{figure}
    }{
        \placeholderimage{#1}{#2}
    }
}

\newcommand{\manualtripleimage}[4]{
    \IfFileExists{#1}{
        \begin{figure}[H]
            \centering
            \includegraphics[width=0.31\textwidth]{#1}\hfill
            \includegraphics[width=0.31\textwidth]{#2}\hfill
            \includegraphics[width=0.31\textwidth]{#3}
            \caption{#4}
        \end{figure}
    }{
        \placeholderimage{#1 / #2 / #3}{#4}
    }
}

\newcommand{\manualtripleimagelabeled}[7]{
    \IfFileExists{#1}{
        \begin{figure}[H]
            \centering
            \begin{minipage}[t]{0.31\textwidth}
                \centering
                \includegraphics[width=\textwidth]{#1}\\[0.15cm]
                \footnotesize #2
            \end{minipage}\hfill
            \begin{minipage}[t]{0.31\textwidth}
                \centering
                \includegraphics[width=\textwidth]{#3}\\[0.15cm]
                \footnotesize #4
            \end{minipage}\hfill
            \begin{minipage}[t]{0.31\textwidth}
                \centering
                \includegraphics[width=\textwidth]{#5}\\[0.15cm]
                \footnotesize #6
            \end{minipage}
            \caption{#7}
        \end{figure}
    }{
        \placeholderimage{#1 / #3 / #5}{#7}
    }
}

\newcommand{\manualdoubleimagelabeled}[5]{
    \IfFileExists{#1}{
        \begin{figure}[H]
            \centering
            \begin{minipage}[t]{0.48\textwidth}
                \centering
                \includegraphics[width=\textwidth]{#1}\\[0.15cm]
                \footnotesize #2
            \end{minipage}\hfill
            \begin{minipage}[t]{0.48\textwidth}
                \centering
                \includegraphics[width=\textwidth]{#3}\\[0.15cm]
                \footnotesize #4
            \end{minipage}
            \caption{#5}
        \end{figure}
    }{
        \placeholderimage{#1 / #3}{#5}
    }
}

\newcommand{\pendingtag}{\textcolor{red}{\textbf{[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]}}}
\newcommand{\manualexterno}[2]{\href{run:#1}{#2}}
\newcommand{\manualnotalinks}{
    \noindent\textbf{Nota sobre los enlaces:} este documento enlaza con otros PDFs del mismo directorio.
    Algunos visores pueden pedir confirmaci\'on antes de abrir archivos locales.\par\medskip
}
\newcommand{\manualnavegacion}{
    \noindent\textbf{Navegacion rapida: }
    \manualexterno{MANUAL_USUARIO_GLOBAL_INSTALACIONES.pdf}{Indice global}
    \textbar\ 
    \manualexterno{MANUAL_USUARIO_AGUA.pdf}{Agua}
    \textbar\ 
    \manualexterno{MANUAL_USUARIO_SANEAMIENTO.pdf}{Saneamiento}
    \textbar\ 
    \manualexterno{MANUAL_USUARIO_VENTILACION.pdf}{Ventilaci\'on}
    \textbar\ 
    \manualexterno{MANUAL_USUARIO_ELECTRICIDAD.pdf}{Electricidad}
    \par\medskip
}
'@

$globalIndex = @'
\section{Particularidades de cada instalaci\'on}

Una vez entendido el funcionamiento general, es mejor consultar cada instalaci\'on en una unidad separada.

Este reparto reduce el tama\~no del manual principal, facilita la revision por especialidad y evita que una correccion local obligue a navegar por un documento demasiado largo.

\subsection{Unidades disponibles}

\begin{itemize}
\item \manualexterno{MANUAL_USUARIO_AGUA.pdf}{Instalaci\'on de Agua}
\item \manualexterno{MANUAL_USUARIO_SANEAMIENTO.pdf}{Instalaci\'on de Saneamiento}
\item \manualexterno{MANUAL_USUARIO_VENTILACION.pdf}{Instalaci\'on de Ventilaci\'on}
\item \manualexterno{MANUAL_USUARIO_ELECTRICIDAD.pdf}{Instalaci\'on de Electricidad}
\end{itemize}

\subsection{Como se relacionan los documentos}

La logica propuesta es esta:

\begin{enumerate}
\item El manual global reune el flujo comun a todas las instalaciones.
\item Cada instalaci\'on mantiene su unidad propia con sus reglas, avisos y capturas especificas.
\item Los enlaces entre PDFs permiten saltar desde el indice global a la unidad que corresponda y volver despues al documento principal.
\end{enumerate}

\subsection{Criterio editorial}

Cuando una regla afecte a todas las instalaciones, debe mantenerse en el manual global.

Cuando una regla dependa del sistema, del catalogo de piezas, de los diametros, de los layers o de avisos especificos, debe ir a la unidad de la instalaci\'on correspondiente.
'@

$globalManual = @'
\documentclass[12pt,a4paper]{article}

\input{comun/preamble.tex}

\title{Manual de Usuario Global de Instalaciones}
\author{}
\date{\today}

\begin{document}

\maketitle
\tableofcontents
\newpage

\manualnotalinks

\input{secciones/manual_global_comun.tex}
\input{secciones/indice_unidades.tex}
\input{secciones/proximas_unidades.tex}

\end{document}
'@

$aguaManual = @'
\documentclass[12pt,a4paper]{article}

\input{comun/preamble.tex}

\title{Manual de Usuario de Agua}
\author{}
\date{\today}

\begin{document}

\maketitle
\manualnotalinks
\manualnavegacion
\tableofcontents
\newpage

\input{secciones/instalacion_agua.tex}

\bigskip
\manualnavegacion

\end{document}
'@

$saneamientoManual = @'
\documentclass[12pt,a4paper]{article}

\input{comun/preamble.tex}

\title{Manual de Usuario de Saneamiento}
\author{}
\date{\today}

\begin{document}

\maketitle
\manualnotalinks
\manualnavegacion
\tableofcontents
\newpage

\input{secciones/instalacion_saneamiento.tex}

\bigskip
\manualnavegacion

\end{document}
'@

$ventilacionManual = @'
\documentclass[12pt,a4paper]{article}

\input{comun/preamble.tex}

\title{Manual de Usuario de Ventilaci\'on}
\author{}
\date{\today}

\begin{document}

\maketitle
\manualnotalinks
\manualnavegacion
\tableofcontents
\newpage

\input{secciones/instalacion_ventilacion.tex}

\bigskip
\manualnavegacion

\end{document}
'@

$electricidadManual = @'
\documentclass[12pt,a4paper]{article}

\input{comun/preamble.tex}

\title{Manual de Usuario de Electricidad}
\author{}
\date{\today}

\begin{document}

\maketitle
\manualnotalinks
\manualnavegacion
\tableofcontents
\newpage

\input{secciones/instalacion_electricidad.tex}

\bigskip
\manualnavegacion

\end{document}
'@

Write-Utf8File -Path (Join-Path $commonDir "preamble.tex") -Content $preamble

Write-Utf8File -Path (Join-Path $sectionsDir "manual_global_comun.tex") -Content $globalCommon
Write-Utf8File -Path (Join-Path $sectionsDir "indice_unidades.tex") -Content $globalIndex
Write-Utf8File -Path (Join-Path $sectionsDir "instalacion_agua.tex") -Content $aguaSection
Write-Utf8File -Path (Join-Path $sectionsDir "instalacion_saneamiento.tex") -Content $saneamientoSection
Write-Utf8File -Path (Join-Path $sectionsDir "instalacion_ventilacion.tex") -Content $ventilacionSection
Write-Utf8File -Path (Join-Path $sectionsDir "instalacion_electricidad.tex") -Content $electricidadSection
Write-Utf8File -Path (Join-Path $sectionsDir "proximas_unidades.tex") -Content $proximasUnidades

Write-Utf8File -Path (Join-Path $texDir "MANUAL_USUARIO_GLOBAL_INSTALACIONES.tex") -Content $globalManual
Write-Utf8File -Path (Join-Path $texDir "MANUAL_USUARIO_AGUA.tex") -Content $aguaManual
Write-Utf8File -Path (Join-Path $texDir "MANUAL_USUARIO_SANEAMIENTO.tex") -Content $saneamientoManual
Write-Utf8File -Path (Join-Path $texDir "MANUAL_USUARIO_VENTILACION.tex") -Content $ventilacionManual
Write-Utf8File -Path (Join-Path $texDir "MANUAL_USUARIO_ELECTRICIDAD.tex") -Content $electricidadManual

Write-Host "Manuales modulares generados en: $texDir"
