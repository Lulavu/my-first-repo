# Bot de noticias de Argentina (Telegram)

Bot que todos los días a las 9am (hora Argentina, GMT-3) manda a tu chat de Telegram
un resumen de 3-5 noticias sobre economía argentina, finanzas personales e
inteligencia artificial, tomadas de RSS de Infobae Economía, El Cronista e iProfesional.

## Archivos

- `bot.py`: lógica del bot (comandos + scheduler + RSS).
- `requirements.txt`: dependencias.
- `Procfile`: comando para correr el worker en Railway/Render.

## Variables de entorno

- `TELEGRAM_TOKEN`: token del bot (te lo dio @BotFather).
- `CHAT_ID`: el chat de Telegram donde se manda el resumen diario.

## 1. Conseguir tu CHAT_ID

1. Deployá el bot (ver pasos abajo) sin la variable `CHAT_ID` todavía, o corré `python bot.py` local con solo `TELEGRAM_TOKEN`.
2. En Telegram, buscá tu bot (`t.me/Novedadeslu_bot`) y mandale `/start`.
3. El bot te va a responder con tu `chat_id`. Copialo.
4. Agregá `CHAT_ID` con ese valor en las variables de entorno del servicio y reiniciá el deploy.

También podés probar el resumen en cualquier momento mandando `/news` al bot.

## 2. Deploy gratis en Railway

1. Creá una cuenta en https://railway.app (podés entrar con GitHub).
2. Click en "New Project" → "Deploy from GitHub repo" → elegí este repositorio.
3. Railway va a detectar el `Procfile` y crear un servicio tipo `worker`.
4. Andá a la pestaña **Variables** del servicio y agregá:
   - `TELEGRAM_TOKEN` = tu token de BotFather
   - `CHAT_ID` = (lo agregás después de hacer `/start`, ver paso 1)
5. En **Settings**, asegurate de que el "Start Command" sea `python bot.py` (o dejá que use el Procfile).
6. Deploy. Mirá los logs para confirmar que arrancó sin errores.
7. Mandale `/start` al bot para obtener el `CHAT_ID`, cargalo en Variables, y Railway va a redeployar solo.

> Nota: el plan gratuito de Railway da un crédito mensual limitado; para un bot liviano como este alcanza sin problema.

## 3. Deploy gratis en Render

1. Creá una cuenta en https://render.com (podés entrar con GitHub).
2. Click en "New +" → "Background Worker".
3. Conectá tu repo de GitHub y seleccioná esta rama.
4. Configurá:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
5. En **Environment**, agregá las variables:
   - `TELEGRAM_TOKEN`
   - `CHAT_ID` (lo completás después de hacer `/start`, ver paso 1)
6. Elegí el plan **Free** y creá el worker.
7. Una vez desplegado, mandale `/start` al bot, copiá el `chat_id`, agregalo como variable de entorno y hacé "Manual Deploy" → "Clear cache & deploy".

## 4. Correr localmente (opcional, para probar)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_TOKEN="tu_token_de_botfather"
export CHAT_ID="tu_chat_id"   # opcional al principio
python bot.py
```

## Notas

- El resumen diario se dispara con `APScheduler` usando la zona horaria `America/Argentina/Buenos_Aires`, así que siempre corre a las 7am hora Argentina sin importar dónde esté deployado el servidor.
- Si un feed RSS falla o cambia de URL, el bot lo ignora y sigue con los demás.
- El comando `/news` sirve para pedir el resumen en cualquier momento (útil para testear).
