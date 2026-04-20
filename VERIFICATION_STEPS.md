# Guía de Verificación de Infraestructura - NotebookUM

Sigue estos pasos para verificar que toda tu infraestructura (Traefik, Redis, PostgreSQL, NotebookUM) está funcionando correctamente.

---

## **PASO 1: Verificar que todos los servicios están levantados**

```powershell
# Ver estado de todos los servicios
docker compose -f dockers/redis/docker-compose.yml ps
docker compose -f dockers/PostgreSQL/docker-compose.yml ps
docker compose -f dockers/traefik/docker-compose.yml ps
docker compose -f dockers/notebookum/docker-compose.yml ps
```

**Esperado:** Todos deben estar con status `Up`.

---

## **PASO 2: Verificar conectividad DNS desde el host**

Edita tu archivo `hosts` en Windows:
```
C:\Windows\System32\drivers\etc\hosts
```

Asegúrate que tenga estas líneas:
```
127.0.0.1 notebookum.universidad.localhost
127.0.0.1 redis.universidad.localhost
127.0.0.1 postgresql.universidad.localhost
127.0.0.1 traefik.universidad.localhost
127.0.0.1 universidad.localhost
```

Luego:
```powershell
# Verifica que se resuelven los nombres
nslookup redis.universidad.localhost
nslookup postgresql.universidad.localhost
nslookup notebookum.universidad.localhost
```

**Esperado:** Todos resuelven a 127.0.0.1

---

## **PASO 3: Probar conexión a Redis vía Traefik**

Instala un cliente Redis en PowerShell:
```powershell
# Opción 1: Redis-CLI desktop o usar Test-NetConnection
Test-NetConnection -ComputerName redis.universidad.localhost -Port 6379

# Opción 2: Usar Docker para conectarse
docker exec redis redis-cli -h localhost -p 6379 -a Qvv3r7y ping
```

**Esperado:** Debes recibir `PONG` como respuesta.

**Contraseña Redis:** `Qvv3r7y`

---

## **PASO 4: Probar conexión a PostgreSQL vía Traefik**

```powershell
# Instala psql si no lo tienes, o usa Docker
# Opción: usar Docker
docker exec postgresql-servidor psql -U notebookum -d notebookum -c "SELECT 1;"
```

**Credenciales PostgreSQL:**
- Usuario: `notebookum`
- Contraseña: `notebookum123`
- Base de datos: `notebookum`
- Puerto: `5432`

**Esperado:** Consulta ejecutada exitosamente.

---

## **PASO 5: Verificar conectividad desde el contenedor de NotebookUM**

```powershell
# Accede al contenedor
docker exec -it notebookum sh

# Dentro del contenedor, prueba ping a los servicios
ping redis
ping postgresql-servidor

# Intenta conexión a Redis
redis-cli -h redis -p 6379 -a Qvv3r7y ping

# Prueba conexión a PostgreSQL
psql -h postgresql-servidor -U notebookum -d notebookum -c "SELECT 1;"
```

**Esperado:** Ambas pruebas funcionan, indicando que están en la misma red virtual.

---

## **PASO 6: Probar acceso HTTP a NotebookUM (local)**

```powershell
# Endpoint de salud sin Traefik (conexión directa)
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health -UseBasicParsing | Select-Object StatusCode, @{Name="Body";Expression={$_.Content | ConvertFrom-Json}}
```

**Esperado:** Status 200 con estado `healthy`.

---

## **PASO 7: Probar acceso HTTPS vía Traefik**

```powershell
# Ignorar validación de certificado autofi  rmado
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

# Prueba con Traefik
$uri = "https://notebookum.universidad.localhost/api/v1/health"
$response = Invoke-WebRequest -Uri $uri -SkipCertificateCheck -UseBasicParsing
Write-Host "Status: $($response.StatusCode)"
Write-Host "Response: $($response.Content)"
```

**Esperado:** Status 200, respuesta desde la app, demostrando que Traefik redirige correctamente.

---

## **PASO 8: Dashboard de Traefik**

Accede al dashboard:
```
http://traefik.universidad.localhost
```

**Esperado:** Ves todos los routers (redis, notebookum, postgresql) configurados correctamente.

---

## **PASO 9: Probar logs de Traefik**

```powershell
docker compose -f dockers/traefik/docker-compose.yml logs -f traefik
```

**Esperado:** Ver logs de tráfico cuando hagas requests.

---

## **PASO 10: Verificación de réplicas (opcional, para balanceo)**

Si quieres probar balanceo de carga con 3-4 instancias de NotebookUM:

```powershell
# Escala a 3 instancias
docker compose -f dockers/notebookum/docker-compose.yml up -d --scale notebookum=3
```

**Esperado:** Traefik automáticamente balancea entre las 3 instancias.

---

## **Checklist Final**

- [ ] Todos los servicios están `Up`
- [ ] DNS resuelve `*.universidad.localhost`
- [ ] Redis responde a ping  
- [ ] PostgreSQL responde consultas
- [ ] Contenedor NotebookUM se conecta a Redis y PostgreSQL  
- [ ] HTTP en localhost:8000 funciona
- [ ] HTTPS vía traefik.universidad.localhost funciona
- [ ] Traefik dashboard es accesible
- [ ] Logs de Traefik muestran tráfico

---

## **Si hay errores:**

### Error: "No such host"
- Verifica el archivo `hosts` de Windows
- Reinicia el cliente DNS: `ipconfig /flushdns`

### Error: "Connection refused"
- Verifica que el servicio está levantado: `docker ps`
- Revisa logs: `docker compose -f dockers/[service]/docker-compose.yml logs`

### Error: "Certificate validation failed"
- Es normal con certificados autofirmados
- Usa `-SkipCertificateCheck` en PowerShell

### Error: "Cannot connect from container"
- Verifica que el contenedor y Traefik están en la misma red: `notebookum-network`
- Usa `docker network inspect notebookum-network` para ver los servicios conectados

---

**¿De qué base estamos?** Todos los servicios están levantados. Comienza por PASO 2 (DNS hosts) y avanza hasta PASO 10.
