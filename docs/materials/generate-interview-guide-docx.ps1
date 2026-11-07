$ErrorActionPreference = 'Stop'

$materialDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$coverPath = Join-Path $materialDir 'RaceOps-Guia-Validacion-Portada.png'
$targetPath = Join-Path $materialDir 'RaceOps-Guia-Validacion-Pilotos.docx'

if (-not (Test-Path -LiteralPath $coverPath)) {
    throw "No se encontró la portada: $coverPath"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("raceops-docx-" + [guid]::NewGuid().ToString('N'))
$wordDir = Join-Path $tempRoot 'word'
$relsDir = Join-Path $tempRoot '_rels'
$wordRelsDir = Join-Path $wordDir '_rels'
$mediaDir = Join-Path $wordDir 'media'
$docPropsDir = Join-Path $tempRoot 'docProps'

New-Item -ItemType Directory -Path $wordDir, $relsDir, $wordRelsDir, $mediaDir, $docPropsDir -Force | Out-Null
Copy-Item -LiteralPath $coverPath -Destination (Join-Path $mediaDir 'cover.png')

$utf8 = [System.Text.UTF8Encoding]::new($false)

function Escape-Xml([string]$value) {
    if ($null -eq $value) { return '' }
    return [System.Security.SecurityElement]::Escape($value)
}

function Add-Paragraph {
    param(
        [Parameter(Mandatory)][string]$Text,
        [string]$Style = 'Normal',
        [string]$Align = '',
        [switch]$KeepNext
    )

    $escaped = Escape-Xml $Text
    $properties = "<w:pStyle w:val=`"$Style`"/>"
    if ($Align) { $properties += "<w:jc w:val=`"$Align`"/>" }
    if ($KeepNext) { $properties += '<w:keepNext/>' }
    return "<w:p><w:pPr>$properties</w:pPr><w:r><w:t xml:space=`"preserve`">$escaped</w:t></w:r></w:p>"
}

function Add-Bullet([string]$Text) {
    return Add-Paragraph -Text ("• " + $Text) -Style 'Bullet'
}

function Add-PageBreak {
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
}

function Add-Callout([string]$Text) {
    $paragraph = Add-Paragraph -Text $Text -Style 'Callout'
    return @"
<w:tbl>
  <w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders><w:left w:val="single" w:sz="18" w:color="20F083"/><w:top w:val="nil"/><w:right w:val="nil"/><w:bottom w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders><w:tblCellMar><w:top w:w="120" w:type="dxa"/><w:left w:w="180" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/><w:right w:w="180" w:type="dxa"/></w:tblCellMar></w:tblPr>
  <w:tr><w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="E9FFF2"/></w:tcPr>$paragraph</w:tc></w:tr>
</w:tbl>
"@
}

function Add-Table {
    param(
        [Parameter(Mandatory)][string[]]$Headers,
        [Parameter(Mandatory)][object[]]$Rows
    )

    $columnWidth = [math]::Floor(10000 / $Headers.Count)
    $grid = ($Headers | ForEach-Object { "<w:gridCol w:w=`"$columnWidth`"/>" }) -join ''
    $headerCells = foreach ($header in $Headers) {
        $text = Escape-Xml $header
        "<w:tc><w:tcPr><w:tcW w:w=`"$columnWidth`" w:type=`"dxa`"/><w:shd w:val=`"clear`" w:color=`"auto`" w:fill=`"0D3B27`"/></w:tcPr><w:p><w:pPr><w:spacing w:after=`"0`"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val=`"D9FFEA`"/></w:rPr><w:t>$text</w:t></w:r></w:p></w:tc>"
    }

    $rowXml = foreach ($row in $Rows) {
        $cells = foreach ($cell in $row) {
            $text = Escape-Xml ([string]$cell)
            "<w:tc><w:tcPr><w:tcW w:w=`"$columnWidth`" w:type=`"dxa`"/><w:shd w:val=`"clear`" w:color=`"auto`" w:fill=`"F5FBF7`"/></w:tcPr><w:p><w:pPr><w:spacing w:after=`"0`"/></w:pPr><w:r><w:t>$text</w:t></w:r></w:p></w:tc>"
        }
        "<w:tr>$($cells -join '')</w:tr>"
    }

    return @"
<w:tbl>
  <w:tblPr><w:tblW w:w="10000" w:type="dxa"/><w:tblBorders><w:top w:val="single" w:sz="5" w:color="86B89C"/><w:left w:val="single" w:sz="5" w:color="86B89C"/><w:bottom w:val="single" w:sz="5" w:color="86B89C"/><w:right w:val="single" w:sz="5" w:color="86B89C"/><w:insideH w:val="single" w:sz="4" w:color="B8D8C5"/><w:insideV w:val="single" w:sz="4" w:color="B8D8C5"/></w:tblBorders><w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr>
  <w:tblGrid>$grid</w:tblGrid>
  <w:tr>$($headerCells -join '')</w:tr>
  $($rowXml -join "`n")
</w:tbl>
"@
}

$body = [System.Collections.Generic.List[string]]::new()

$body.Add(@'
<w:p>
  <w:pPr><w:jc w:val="center"/><w:spacing w:after="0"/></w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="6648000" cy="9401000"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="1" name="Portada RaceOps"/>
        <wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr><pic:cNvPr id="0" name="cover.png"/><pic:cNvPicPr/></pic:nvPicPr>
              <pic:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
              <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="6648000" cy="9401000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
'@)
$body.Add((Add-PageBreak))

$body.Add((Add-Paragraph -Text '01 · OBJETIVO DE MISIÓN' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text 'Validar el flujo, no buscar aprobación' -Style 'Title'))
$body.Add((Add-Callout -Text 'No preguntaremos “¿te gusta RaceOps?”. Pediremos que nos muestren cómo ocurre una sesión real y dónde nuestro modelo se equivoca.'))
$body.Add((Add-Paragraph -Text 'Lo que RaceOps busca resolver' -Style 'Heading1'))
@(
    'Conectar feedback, datos y observaciones.',
    'Convertir análisis en prioridades.',
    'Relacionar una acción con su resultado.',
    'Conservar aprendizaje por pista y vehículo.',
    'Proteger información técnica confidencial.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Lo que RaceOps no pretende' -Style 'Heading1'))
@(
    'Reemplazar MyChron, RaceStudio o MoTeC.',
    'Capturar toda la telemetría.',
    'Imitar software profesional de Formula 1.',
    'Obligar a completar formularios largos.',
    'Suponer que todos los equipos lo necesitan.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Pregunta central' -Style 'Heading1'))
$body.Add((Add-Paragraph -Text '¿Puede RaceOps conservar el razonamiento entre sesiones sin añadir más trabajo del valor que aporta?' -Style 'Quote' -Align 'center'))
$body.Add((Add-Paragraph -Text 'Estado actual de la evidencia' -Style 'Heading1'))
$body.Add((Add-Table -Headers @('Afirmación', 'Estado') -Rows @(
    @('Feedback y datos se complementan.', 'Respaldado'),
    @('Diferentes roles necesitan información diferente.', 'Respaldado'),
    @('Existe fragmentación relevante en todos los equipos.', 'Parcialmente respaldado'),
    @('RaceOps será utilizado repetidamente.', 'Hipótesis'),
    @('Existe disposición a pagar.', 'Hipótesis comercial')
)))

$body.Add((Add-PageBreak))
$body.Add((Add-Paragraph -Text '02 · SOLICITUD DE APOYO' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text 'Mensaje para los pilotos' -Style 'Title'))
$messageParagraphs = @(
    'Hola, [nombre]. Muchas gracias nuevamente por la información que me compartiste sobre cómo trabajan después de una sesión. Me ayudó a cambiar bastante el enfoque de RaceOps.',
    'Ahora la idea no es reemplazar MyChron, RaceStudio, MoTeC ni la telemetría. RaceOps busca relacionar lo que sintió el piloto, lo que mostraron los datos, lo que decidió el equipo y lo que ocurrió en la siguiente sesión.',
    'Antes de desarrollar quiero comprobar que no estoy imaginando un proceso alejado de la realidad. ¿Podrías ayudarme con una conversación de aproximadamente 20 minutos para revisar el flujo?',
    'Me interesa especialmente que me digas qué entendí mal, qué pasos no suceden realmente, qué información sobra, qué sería incómodo registrar, qué debería ser confidencial y qué tendría que hacer RaceOps para ser práctico.',
    'Puede ser por llamada, mensajes o audios, como te resulte más cómodo. No necesito información sensible del equipo y cualquier ejemplo puede mantenerse anónimo.',
    'Gracias por ayudarme a construir algo basado en la realidad y no solamente en suposiciones.'
)
foreach ($paragraph in $messageParagraphs) { $body.Add((Add-Paragraph -Text $paragraph -Style 'Message')) }
$body.Add((Add-Paragraph -Text 'Personalización para experiencia profesional' -Style 'Heading2'))
$body.Add((Add-Paragraph -Text 'También me interesa entender cómo cambia este proceso según el nivel del equipo y qué partes sólo tendrían sentido en categorías profesionales.'))
$body.Add((Add-Paragraph -Text 'Personalización para karting y fórmula' -Style 'Heading2'))
$body.Add((Add-Paragraph -Text 'Me ayudaría conocer qué partes cambian entre karting y fórmula, para no diseñar un sistema demasiado rígido.'))
$body.Add((Add-Paragraph -Text 'Seguimiento breve' -Style 'Heading2'))
$body.Add((Add-Paragraph -Text 'Hola, [nombre]. Sólo retomo el mensaje anterior. No hay problema si ahora no tienes tiempo; también me ayudaría mucho si pudieras responder mediante audios cuando tengas oportunidad. Gracias nuevamente.' -Style 'Message'))
$body.Add((Add-Callout -Text 'Pedir 20 minutos, ofrecer anonimato y facilitar llamada, texto o audio. No enviar todavía toda la documentación técnica.'))

$body.Add((Add-PageBreak))
$body.Add((Add-Paragraph -Text '03 · RECONSTRUCCIÓN DEL TRABAJO REAL' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text 'Antes de mostrar RaceOps' -Style 'Title'))
$body.Add((Add-Paragraph -Text 'Pide que recuerden una sesión reciente y concreta. Las historias reales valen más que las opiniones generales.'))
$body.Add((Add-Paragraph -Text 'Desde que baja del vehículo' -Style 'Heading1'))
@(
    '¿Qué ocurrió desde que bajaste del vehículo hasta la siguiente sesión?',
    '¿Con quién hablaste primero?',
    '¿Qué información proporcionaste como piloto?',
    '¿Qué herramientas revisó el equipo?',
    '¿Quién tomó notas y dónde las guardó?',
    '¿Qué información quedó solamente en una conversación?',
    '¿Qué decisión se tomó para la siguiente sesión?',
    '¿Cómo se comunicó esa decisión al piloto y al mecánico?',
    '¿Cómo comprobaron después si el cambio funcionó?',
    '¿La conclusión quedó registrada en algún lugar?'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Herramientas y memoria' -Style 'Heading1'))
@(
    '¿Qué información guardan en MyChron, RaceStudio, MoTeC, hojas de cálculo, papel o mensajes?',
    '¿Qué herramienta funciona suficientemente bien y no reemplazarías?',
    '¿Qué información resulta difícil recuperar después?',
    '¿Han buscado qué hicieron la última vez que visitaron una pista?',
    '¿Cuánto tardaron en encontrarlo?',
    '¿Qué información nunca escriben porque tomaría demasiado tiempo?',
    '¿Qué información se captura dos veces?',
    '¿Qué proceso manual causa más molestias?',
    '¿Qué parte del proceso funciona perfectamente y no necesita software adicional?'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Callout -Text 'Seguimiento: ¿cuándo ocurrió?, ¿es habitual o una excepción?, ¿quién registra la información y qué pasa si esa persona no está?'))

$body.Add((Add-PageBreak))
$body.Add((Add-Paragraph -Text '04 · PRUEBA DEL FLUJO' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text 'Ahora sí: mostrar una sola misión' -Style 'Title'))
$body.Add((Add-Callout -Text 'Crear sesión → vueltas y sectores → feedback → observaciones → hipótesis → hasta tres prioridades → siguiente sesión → comparación → conclusión.'))
$body.Add((Add-Paragraph -Text 'Preguntas para destruir supuestos' -Style 'Heading1'))
@(
    '¿Qué parte de este flujo está equivocada?',
    '¿Qué paso no ocurre así en un equipo real?',
    '¿Qué falta?',
    '¿Qué información estaríamos capturando dos veces?',
    '¿En qué momento exacto se utilizaría RaceOps?',
    '¿Quién sería responsable de registrar cada parte?',
    '¿Qué información debería poder registrar el piloto?',
    '¿Qué información no debería ver el piloto?',
    '¿Qué debería ver solamente ingeniería?',
    '¿Qué campos serían demasiado molestos durante un evento?',
    'Si tuvieras que eliminar la mitad del flujo, ¿qué conservarías?',
    '¿Qué haría que el equipo dejara de utilizarlo después de dos eventos?'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Prueba práctica posterior' -Style 'Heading1'))
$body.Add((Add-Paragraph -Text 'Tarea: Acabas de terminar una sesión. Registra que sentiste inestabilidad trasera al frenar en T4, revisa los resultados disponibles y crea una prioridad para la siguiente sesión.' -Style 'Message'))
$body.Add((Add-Paragraph -Text 'Durante la tarea observar' -Style 'Heading2'))
@(
    'Tiempo necesario para completar la tarea.',
    'Puntos donde duda o se detiene.',
    'Campos que ignora o cuestiona.',
    'Palabras que no comprende.',
    'Errores o caminos diferentes a los esperados.',
    'Ayuda necesaria para terminar.',
    'Comportamiento desde un teléfono o bajo presión.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }

$body.Add((Add-PageBreak))
$body.Add((Add-Paragraph -Text '05 · FUERZA DE LAS SEÑALES' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text '¿De verdad se utilizaría?' -Style 'Title'))
$body.Add((Add-Paragraph -Text 'No todas las respuestas pesan igual. La conducta observable tiene más valor que una opinión amable.'))
$body.Add((Add-Table -Headers @('Señal observada', 'Valor') -Rows @(
    @('“Suena interesante”.', 'Muy bajo'),
    @('“Creo que lo usaría”.', 'Bajo'),
    @('Corrige el flujo con ejemplos reales.', 'Medio'),
    @('Comparte datos anónimos para probarlo.', 'Alto'),
    @('Utiliza el prototipo durante una sesión.', 'Muy alto'),
    @('Regresa posteriormente a consultar el historial.', 'Evidencia fuerte'),
    @('Pide utilizarlo nuevamente.', 'Evidencia muy fuerte')
)))
$body.Add((Add-Paragraph -Text 'Escala de validación' -Style 'Heading1'))
@(
    'Una entrevista: señal; no generalizar.',
    'Dos o tres participantes independientes: candidato a patrón.',
    'Cinco o más participantes de distintos roles: patrón con mayor respaldo.',
    'Uso observado en contexto real: evidencia más valiosa disponible.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Registrar por cada hallazgo' -Style 'Heading1'))
@(
    'Rol, categoría y contexto del participante.',
    'Ejemplo concreto y fecha aproximada.',
    'Frecuencia con la que ocurre.',
    'Herramienta utilizada actualmente.',
    'Consecuencia real del problema.',
    'Quién necesita y quién no debe ver la información.',
    'Clasificación: respaldado, parcial, hipótesis o rechazado.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }

$body.Add((Add-PageBreak))
$body.Add((Add-Paragraph -Text '06 · PROTOCOLO DE AJUSTE' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text 'Cómo cambiar RaceOps según la realidad' -Style 'Title'))
$body.Add((Add-Table -Headers @('Si descubrimos que…', 'Entonces ajustamos…') -Rows @(
    @('Nadie registra después de una sesión.', 'Identificar responsable real o reducir el flujo.'),
    @('El piloto sólo habla y no escribe.', 'Captura rápida por otro rol o selecciones breves.'),
    @('El tiempo entre sesiones es mínimo.', 'Nota mínima inmediata y análisis detallado posterior.'),
    @('RaceStudio ya conserva las notas necesarias.', 'Referenciar o complementar; no duplicar.'),
    @('La confidencialidad es crítica.', 'Reforzar vistas y pruebas por rol.'),
    @('Nadie consulta el historial.', 'Reducir su prioridad y buscar el motivo.'),
    @('Los sectores son suficientes para coaching.', 'No importar canales innecesarios.'),
    @('Mantenimiento concentra el valor.', 'Conectar síntomas, incidentes y reparaciones.'),
    @('El flujo completo es demasiado largo.', 'Separar captura rápida de análisis posterior.')
)))
$body.Add((Add-Paragraph -Text 'Principios de facilidad' -Style 'Heading1'))
@(
    'Defaults: no pedir información que ya conocemos.',
    'Plantillas: reutilizar formatos del equipo.',
    'Acciones rápidas: operaciones frecuentes a un toque.',
    'Copiar anterior: partir de la sesión anterior.',
    'Contexto automático: usuario, fecha y asociaciones.',
    'Notas breves: evitar formularios enciclopédicos.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Callout -Text 'Cada campo manual debe justificar qué decisión ayuda a tomar o qué aprendizaje permite conservar.'))

$body.Add((Add-PageBreak))
$body.Add((Add-Paragraph -Text '07 · CIERRE Y SIGUIENTE MISIÓN' -Style 'Eyebrow'))
$body.Add((Add-Paragraph -Text 'Comercialización: todavía una hipótesis' -Style 'Title'))
$body.Add((Add-Paragraph -Text 'No comenzar preguntando cuánto pagarían. Primero debemos demostrar que el problema es frecuente y que RaceOps mejora el trabajo.'))
$body.Add((Add-Paragraph -Text 'Preguntas comerciales posteriores' -Style 'Heading1'))
@(
    '¿Quién decide comprar herramientas dentro del equipo?',
    '¿Qué problema tendría que evitar para justificar un gasto?',
    '¿Contra qué costo se compararía?',
    '¿Se preferiría pagar por equipo, vehículo o temporada?',
    '¿Qué evidencia necesitarían antes de probar una herramienta nueva?'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Checklist de la conversación' -Style 'Heading1'))
@(
    '□ Pedí permiso para tomar notas.',
    '□ Evité solicitar información sensible.',
    '□ Partí de una sesión real.',
    '□ Pregunté por herramientas actuales.',
    '□ Busqué contraevidencia.',
    '□ No defendí la aplicación.',
    '□ Pregunté qué eliminar.',
    '□ Identifiqué al responsable real.',
    '□ Registré ejemplos concretos.',
    '□ Pedí permiso para un seguimiento.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'Después de la entrevista' -Style 'Heading1'))
@(
    'Documentar la entrevista como INT-XXX.',
    'Separar observación, interpretación e hipótesis.',
    'Registrar evidencia y contraevidencia.',
    'Enviar un resumen para confirmar que entendimos correctamente.',
    'Actualizar requisitos solamente cuando la evidencia lo justifique.'
) | ForEach-Object { $body.Add((Add-Bullet $_)) }
$body.Add((Add-Paragraph -Text 'RaceOps no gana por parecer sofisticado. Gana si un equipo puede recordar qué ocurrió, qué cambió y qué aprendió.' -Style 'Quote' -Align 'center'))
$body.Add((Add-Callout -Text 'Siguiente paso: enviar el mensaje, agendar 20 minutos y regresar con notas. Cada entrevista mejora el rumbo antes de que el código vuelva costoso cambiarlo.'))

$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    $($body -join "`n")
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/>
      <w:cols w:space="720"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:body>
</w:document>
"@

$stylesXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI"/><w:sz w:val="21"/><w:color w:val="183128"/><w:lang w:val="es-MX"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="100" w:line="280" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="80" w:after="180"/></w:pPr><w:rPr><w:rFonts w:ascii="Segoe UI Semibold" w:hAnsi="Segoe UI Semibold"/><w:b/><w:color w:val="0D6B3A"/><w:sz w:val="40"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="80"/></w:pPr><w:rPr><w:rFonts w:ascii="Segoe UI Semibold" w:hAnsi="Segoe UI Semibold"/><w:b/><w:color w:val="0D6B3A"/><w:sz w:val="29"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="150" w:after="60"/></w:pPr><w:rPr><w:b/><w:color w:val="168A50"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Eyebrow"><w:name w:val="Eyebrow"/><w:basedOn w:val="Normal"/><w:next w:val="Title"/><w:pPr><w:keepNext/><w:spacing w:after="50"/></w:pPr><w:rPr><w:b/><w:color w:val="20A963"/><w:sz w:val="17"/><w:caps/><w:spacing w:val="18"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Bullet"><w:name w:val="Bullet"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360" w:hanging="220"/><w:spacing w:after="55"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="160" w:after="160"/></w:pPr><w:rPr><w:i/><w:color w:val="0D6B3A"/><w:sz w:val="27"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Callout"><w:name w:val="Callout"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="0"/></w:pPr><w:rPr><w:b/><w:color w:val="0B5C35"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Message"><w:name w:val="Message"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="240" w:right="240"/><w:spacing w:before="50" w:after="100"/></w:pPr><w:rPr><w:color w:val="234B37"/><w:sz w:val="20"/></w:rPr></w:style>
</w:styles>
'@

$contentTypes = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
'@

$packageRels = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
'@

$documentRels = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/cover.png"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>
'@

$settingsXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="720"/>
  <w:doNotCompressPictures/>
  <w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>
</w:settings>
'@

$created = [DateTime]::UtcNow.ToString('s') + 'Z'
$coreXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>RaceOps — Guía de validación con pilotos</dc:title>
  <dc:subject>Product Discovery y entrevistas</dc:subject>
  <dc:creator>RaceOps</dc:creator>
  <cp:keywords>RaceOps, motorsport, karting, entrevistas, validación</cp:keywords>
  <dc:description>Guía editable para validar el flujo de RaceOps con pilotos y equipos.</dc:description>
  <dcterms:created xsi:type="dcterms:W3CDTF">$created</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">$created</dcterms:modified>
</cp:coreProperties>
"@

$appXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office Word</Application>
  <AppVersion>16.0000</AppVersion>
  <Company>RaceOps</Company>
</Properties>
'@

[System.IO.File]::WriteAllText((Join-Path $tempRoot '[Content_Types].xml'), $contentTypes, $utf8)
[System.IO.File]::WriteAllText((Join-Path $relsDir '.rels'), $packageRels, $utf8)
[System.IO.File]::WriteAllText((Join-Path $wordDir 'document.xml'), $documentXml, $utf8)
[System.IO.File]::WriteAllText((Join-Path $wordDir 'styles.xml'), $stylesXml, $utf8)
[System.IO.File]::WriteAllText((Join-Path $wordDir 'settings.xml'), $settingsXml, $utf8)
[System.IO.File]::WriteAllText((Join-Path $wordRelsDir 'document.xml.rels'), $documentRels, $utf8)
[System.IO.File]::WriteAllText((Join-Path $docPropsDir 'core.xml'), $coreXml, $utf8)
[System.IO.File]::WriteAllText((Join-Path $docPropsDir 'app.xml'), $appXml, $utf8)

if (Test-Path -LiteralPath $targetPath) {
    throw "El documento ya existe: $targetPath"
}

Add-Type -AssemblyName System.IO.Compression
$targetStream = [System.IO.File]::Open($targetPath, [System.IO.FileMode]::CreateNew)
$archive = [System.IO.Compression.ZipArchive]::new(
    $targetStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $false
)

try {
    Get-ChildItem -LiteralPath $tempRoot -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($tempRoot.Length).TrimStart('\').Replace('\', '/')
        $entry = $archive.CreateEntry($relativePath, [System.IO.Compression.CompressionLevel]::Optimal)
        $entryStream = $entry.Open()
        $sourceStream = [System.IO.File]::OpenRead($_.FullName)
        try {
            $sourceStream.CopyTo($entryStream)
        }
        finally {
            $sourceStream.Dispose()
            $entryStream.Dispose()
        }
    }
}
finally {
    $archive.Dispose()
    $targetStream.Dispose()
}

Write-Output $targetPath
