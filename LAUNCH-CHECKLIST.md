# UnpackInsurance: guía de lanzamiento paso a paso (titular residente en España)

> Orientación práctica, no asesoramiento legal ni fiscal. Confirma los puntos fiscales con un gestor y los legales con un abogado.

---

## Paso 1. Comprobar y asegurar el nombre
1. Busca `unpackinsurance.com` en Namecheap, Cloudflare Registrar o Porkbun. Si está libre, cómpralo (unos 10–15 €/año).
2. Busca "unpackinsurance" y "unpack insurance" en https://tmsearch.uspto.gov (EE. UU.). Revisa sobre todo la clase 36 (seguros y finanzas).
3. Opcional: busca también en EUIPO (https://euipo.europa.eu/eSearch) y en la OEPM.
4. Opcional, cuando haya ingresos: registrar tu propia marca en la OEPM o la EUIPO.

## Paso 2. Darte de alta en Hacienda (antes de cobrar el primer euro)
Los ingresos de AdSense son una actividad económica.

1. **Alta censal (modelo 036)** en la sede de la Agencia Tributaria, o a través de un gestor.
   - Epígrafe de IAE: lo habitual para webs con publicidad es el **844 (Servicios de publicidad, relaciones públicas y similares)**. Confírmalo con tu gestor.
   - Marca la casilla de inscripción en el **ROI (Registro de Operadores Intracomunitarios)**. Te paga Google Ireland Ltd., una empresa de otro país de la UE, así que la operación va sin IVA español (inversión del sujeto pasivo) y hay que declararla en el **modelo 349**.
2. **Seguridad Social**: si la actividad es habitual, normalmente corresponde el alta en el **RETA (autónomos)**. Existe una cuota reducida ("tarifa plana") para nuevos autónomos. Consulta tu caso con el gestor.
3. **Declaraciones habituales** (tu gestor te dirá cuáles te aplican):
   - Modelo 303 (IVA, trimestral)
   - Modelo 349 (operaciones intracomunitarias)
   - Modelo 130 (pago fraccionado del IRPF)
   - La declaración de la renta anual
4. **Guarda los justificantes** de pago de AdSense y de tus gastos deducibles: dominio, hosting, gestor, etc.

## Paso 3. Hosting, dominio y correo
1. Hosting estático gratuito con HTTPS:
   - **Cloudflare Pages** o **Netlify**: conecta el repo de GitHub, sin comando de build, directorio `/`.
   - Ambos sirven `404.html` automáticamente.
2. Apunta el dominio al hosting y comprueba que carga con `https://`.
3. Email con tu dominio, por ejemplo `hello@unpackinsurance.com`:
   - Cloudflare Email Routing (gratis, reenvía a tu Gmail)
   - Zoho Mail o Google Workspace
4. Acepta el acuerdo de tratamiento de datos (DPA) del hosting. Suele estar en sus términos o en el panel.

## Paso 4. Rellenar todos los marcadores
Haz buscar y reemplazar en todo el proyecto. Para encontrarlos: `grep -rn "\[[A-Z]" .`

| Marcador | Qué poner |
|---|---|
| `[OWNER NAME]` | Tu nombre y apellidos completos (o la razón social si creas una S.L.) |
| `[NIF]` | Tu NIF (o el CIF de la sociedad) |
| `[POSTAL ADDRESS]` | Dirección postal. La LSSI exige un domicilio; si no quieres publicar tu casa, consulta con el abogado si puedes usar un domicilio profesional |
| `[CITY]` | Ciudad para la cláusula de tribunales (aviso legal y términos) |
| `[CONTACT EMAIL]` | Tu email de contacto |
| ~~`unpackinsurance.com`~~ | Hecho: `unpackinsurance.com` |
| `[EFFECTIVE DATE]` | Fecha de publicación de los textos legales |
| `[HOSTING PROVIDER]` | Por ejemplo "Cloudflare, Inc." o "Netlify, Inc." |
| `[FORM PROVIDER]` | Por ejemplo "Formspree, Inc." (o quita esa línea si no usas el formulario) |
| `[LOG RETENTION, e.g. 30 days]`, `[ANALYTICS RETENTION, e.g. 14 months]` | Los plazos reales de tus proveedores |
| `[CARRIER A]`, `[CARRIER B]`, `[CARRIER C]` | Cámbialo por texto genérico ("several providers") mientras no tengas acuerdos con aseguradoras |
| `ca-pub-XXXXXXXXXXXXXXXX` | Tu ID de editor de AdSense (en todos los HTML) |
| `pub-XXXXXXXXXXXXXXXX` | El mismo ID en `ads.txt` |
| Bloques `[PLACEHOLDER: …]` y la caja amarilla de privacidad | Bórralos cuando hayas completado lo que indican |

## Paso 5. Formulario de contacto
- Mientras `data-endpoint` esté vacío en `contact.html`, el formulario no se muestra y la página solo ofrece el email. Esto ya es correcto legalmente.
- Para activarlo:
  1. Crea un formulario gratuito en https://formspree.io.
  2. Copia la URL (`https://formspree.io/f/xxxxxxx`) en `data-endpoint="..."`.
  3. Pon "Formspree, Inc." en `[FORM PROVIDER]`.
- El formulario ya incluye la casilla obligatoria de aceptación de la privacidad y la información básica de protección de datos.

## Paso 6. Protección de datos (RGPD y LOPDGDD)
1. Usa la herramienta gratuita **Facilita RGPD** de la AEPD (https://www.aepd.es) para generar tu registro básico de actividades de tratamiento. Para una web pequeña tarda unos 15 minutos.
2. Guarda los DPA de tus proveedores (hosting, Formspree; Google los incluye en los términos de AdSense).
3. Atiende las solicitudes de derechos (acceso, supresión…) en el plazo de **un mes**.
4. No necesitas Delegado de Protección de Datos (DPO) para una web de este tamaño.

## Paso 7. Solicitar y configurar AdSense
1. Antes de solicitar, comprueba que:
   - no quedan marcadores visibles en la web;
   - el dominio es propio y carga con HTTPS;
   - eres mayor de 18 años.
2. AdSense → **Sites** → añade `unpackinsurance.com`. Para verificar el sitio elige el método **"Meta tag"**: la etiqueta ya está en todas las páginas, solo tienes que poner tu ID.
3. Publica `ads.txt` con tu ID y comprueba que abre en `https://unpackinsurance.com/ads.txt`.
4. **Privacy & messaging** (imprescindible en España):
   - Crea el mensaje **"European regulations"** (RGPD) para EEE, Reino Unido y Suiza. Activa el botón **"Do not consent"**: la AEPD exige que rechazar sea tan fácil como aceptar.
   - Crea el mensaje **"US state regulations"** para las leyes de privacidad de EE. UU.
   - El botón "Privacy settings" del pie ya reabre ese mensaje automáticamente.
5. **Payments**:
   - Información fiscal: **formulario W-8BEN** como persona física no estadounidense, con tu NIF español. El convenio España–EE. UU. puede reducir la retención sobre los ingresos de visitantes de EE. UU.
   - Datos bancarios (IBAN).
   - Verificación por PIN, que llega por correo postal.
6. Tras la aprobación:
   - Activa **Auto ads**.
   - Opcional: crea bloques "Display" y pega sus IDs en `AD_SLOTS` (`js/integrations.js`).
7. Nunca hagas clic en tus propios anuncios ni pidas a otros que lo hagan. Es la causa más común de cierre de cuentas.

## Paso 8. SEO y tráfico orgánico
1. **Google Search Console**: verifica el dominio por DNS y envía `https://unpackinsurance.com/sitemap.xml`.
2. **Bing Webmaster Tools**: importa la configuración desde Search Console.
3. Prueba una guía en el **Rich Results Test** de Google.
4. Opcional, **Google Analytics 4**:
   - Pon el ID en `GA_MEASUREMENT_ID` (`js/integrations.js`).
   - Revisa la fila de "Analytics" en la política de privacidad y la tabla de cookies.
5. Publica 1–2 guías nuevas por semana. Lo ideal es tener entre 20 y 30 antes de solicitar AdSense.
6. Añade autores reales con biografía en "About". En temas de dinero y seguros, Google valora mucho la experiencia demostrable.

## Paso 9. Revisión legal final (recomendada)
Pide a un abogado de derecho digital que revise:
- `legal-notice.html` (aviso legal, LSSI)
- `privacy-policy.html` (RGPD y leyes de EE. UU.)
- `cookie-policy.html`
- `terms.html`
- `do-not-sell.html`

Suele ser un servicio de precio cerrado.

## Paso 10. Mantenimiento
- Revisa los textos legales una vez al año y cada vez que añadas un servicio nuevo (analítica, newsletter, afiliación…).
- **Antes de cobrar comisiones de aseguradoras o de captación de clientes**, comprueba los requisitos de licencia de agente en cada estado de EE. UU. Mientras solo uses AdSense no hace falta licencia.
- La cabecera y el pie están copiados en cada HTML: cámbialos con buscar y reemplazar en todos los archivos.
- Las tarifas de `js/calculator.js` son de ejemplo, no datos actuariales.
