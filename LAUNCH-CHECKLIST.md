# Checklist de lanzamiento

## 1. Reemplazar marcadores (buscar y reemplazar en todo el proyecto)
| Marcador | Qué poner |
|---|---|
| ~~`[BRAND NAME]`~~ | Hecho: PlainCover |
| `[DOMAIN]` | Dominio sin `https://` (ej. `example.com`) |
| `[CONTACT EMAIL]` | Email de contacto |
| `[COMPANY LEGAL NAME]`, `[COMPANY ADDRESS]` | Empresa y dirección |
| `[EFFECTIVE DATE]`, `[GOVERNING STATE]` | Páginas legales |
| `[CARRIER A]`, `[CARRIER B]`, `[CARRIER C]` | Aseguradoras con las que tengas acuerdo, o texto genérico ("several providers") |
| `ca-pub-XXXXXXXXXXXXXXXX` | ID de editor de AdSense (todas las páginas HTML) |
| `pub-XXXXXXXXXXXXXXXX` | El mismo ID en `ads.txt` |
| Bloques `[PLACEHOLDER: …]` | Texto legal revisado por un abogado |

Después: `site.webmanifest` (nombre) y, si quieres, regenerar `images/og-image.png` con tu marca.

## 2. Antes de solicitar AdSense
- Dominio propio con HTTPS (AdSense no aprueba subdominios gratuitos de hosting).
- Sin marcadores visibles: Google rechaza sitios con contenido "en construcción".
- Privacidad con la sección de AdSense (ya incluida, revisar), Contacto y About completos.
- Formulario de contacto conectado (Formspree, Netlify Forms, etc.) o eliminar el formulario y dejar solo el email.
- Recomendado: autores reales con biografía y, si es posible, revisión por un agente con licencia (el contenido de seguros es YMYL).
- Recomendado: 20–30 artículos antes de solicitar; hay 10 guías + glosario.

## 3. Activar anuncios
1. AdSense > Sites > añadir el dominio. Verificación: método "Meta tag" (ya está en cada página).
2. Publicar `ads.txt` con tu ID en la raíz.
3. Tras la aprobación: activar Auto ads en AdSense.
4. Opcional: crear unidades "Display" y pegar los IDs en `AD_SLOTS` de `js/integrations.js`.
5. AdSense > Privacy & messaging: activar mensaje de consentimiento (EEE/UK/Suiza) y mensaje de regulaciones estatales de EE. UU.

## 4. SEO
1. Google Search Console: verificar dominio (DNS) y enviar `https://TU-DOMINIO/sitemap.xml`.
2. Bing Webmaster Tools: importar desde Search Console.
3. Probar una guía en el Rich Results Test de Google (datos estructurados Article + BreadcrumbList).
4. Opcional: GA4, pegar el ID en `GA_MEASUREMENT_ID` de `js/integrations.js` y describirlo en la privacidad.
5. Publicar 1–2 guías nuevas por semana. Al añadir páginas: copiar una guía existente, cambiar título, descripción, canonical, fechas y JSON-LD, y añadirla a `sitemap.xml` y `guides/index.html`.

## 5. Notas de mantenimiento
- Cabecera y pie están en cada HTML: los cambios se hacen con buscar y reemplazar en todos los archivos.
- Las tarifas de la calculadora (`js/calculator.js`) son de ejemplo, no datos actuariales.
