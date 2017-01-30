# qgis-GeoDanmarkCheck

[![Build Status](https://travis-ci.org/Septima/qgis-GeoDanmarkCheck.svg?branch=master)](https://travis-ci.org/Septima/qgis-GeoDanmarkCheck)
[![Gitter](https://badges.gitter.im/Septima/qgis-GeoDanmarkCheck.svg)](https://gitter.im/Septima/qgis-GeoDanmarkCheck?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Plugin for validating GeoDanmark data

## Installation
- Hent kildekoden fra dette repositiory 
  - Øverst til højre på [forsiden](https://github.com/Septima/qgis-GeoDanmarkCheck) klikkes "Clone or Download" og derefter "Download zip" 
  - Pak zip-filen ud
- Kopier underbiblioteket `GeoDanmarkChecker` til QGIS´ plugin folder (se herunder)
- Aktivér pluginet i QGIS
  - Klik "Plugins->Manage and Install Plugins" 
  - Gå til fanen "Installed" 
  - Sæt hak ud for pluginet (kaldet `GeoDanmark Checker`)

På Windows findes QGIS´ pluginmappe under `C:\Users\USERNAME\.qgis2\python`, hvor `USERNAME` er dit brugernavn.

## Opdatering
Når først pluginet er korrekt installeret kan det opdateres inde fra QGIS på følgende måde
- Klik "Plugins->GeoDanmark Checker->Update Plugin"
- Klik på det release, du vil opdatere til, eller "Latest development version", hvis du vil opdatere til udviklingsversionen
- Det kan i nogle tilfælde være nødvendigt at genstarte QGIS for at ændringerne træder i kraft
