# OCRFactura — Guía rápida

Esta aplicación te ayuda a pasar datos de tickets (recibos) a Excel para facturación. Usas ChatGPT para extraer los datos de las fotos de los tickets; luego pegas el resultado aquí y exportas un archivo Excel.

---

## Cómo abrir la aplicación

- **Desde el ícono del escritorio (recomendado):** haz doble clic en **OCRFactura**. Se abrirá tu navegador; no verás ninguna ventana negra.
- **Desde la carpeta:** haz doble clic en **OCRFactura.exe**. Verás una ventanita de consola y se abrirá el navegador. Puedes cerrar la aplicación cerrando esa ventanita.

---

## Pasos para usar la aplicación

1. En la página que se abrió, **copia el texto del “Prompt para ChatGPT”** (el cuadro largo).
2. Entra a **ChatGPT**, sube **3 a 5 fotos de tickets** y pega ese prompt. Envía.
3. ChatGPT te devolverá un **JSON**. Cópialo completo (solo el JSON, sin explicaciones).
4. En OCRFactura, **pega ese JSON** en el cuadro y haz clic en **Add Batch**. Repite con más lotes si quieres.
5. Cuando tengas todos los lotes, haz clic en **Export Excel**. Se generará un archivo Excel en la carpeta **output** (dentro de la misma carpeta donde está la aplicación).
6. Si quieres ver un resumen visual, usa el botón **Visualize** y elige el archivo Excel.

---

## Dónde se guardan los archivos

- **Excel exportados:** carpeta **output** (junto a la aplicación).  
  Ejemplo: `C:\...\OCRFactura\output\MonthlyInvoicing_2026-02_123456.xlsx`
- **Sesión del día:** en `output\sessions\` (un archivo por día). No hace falta abrirlos a mano.

---

## Cómo cerrar la aplicación

- Si abriste con **el ícono del escritorio:** cierra la pestaña del navegador cuando termines. La aplicación sigue corriendo en segundo plano. Para detenerla por completo, abre el **Administrador de tareas** (Ctrl+Mayús+Esc), busca **OCRFactura.exe** y haz clic en “Finalizar tarea”.
- Si abriste con **doble clic en OCRFactura.exe:** cierra la **ventanita negra** (consola) y la aplicación se cerrará.

---

## Si algo falla

- Asegúrate de haber copiado **solo el JSON** de ChatGPT (sin texto como “Aquí está el JSON…”).
- Si la página no carga, revisa que ningún otro programa esté usando el puerto (por ejemplo, otra instancia de OCRFactura). Cierra la otra o reinicia el equipo y vuelve a abrir OCRFactura.
