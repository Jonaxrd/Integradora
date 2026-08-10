# SCOPE Hardware Scanner

SCOPE es un sistema de análisis de hardware orientado a detectar los principales componentes de una computadora, evaluar su estado general y generar recomendaciones de actualización de acuerdo con el presupuesto disponible del usuario.

El proyecto combina una aplicación de escritorio desarrollada en Python, un motor de recomendaciones, una base de datos MongoDB Atlas y una Progressive Web App (PWA) para ofrecer una experiencia completa de análisis y recomendación de hardware.

---

## Objetivo

Desarrollar una solución capaz de analizar el hardware de una computadora y proporcionar recomendaciones de actualización comprensibles, útiles y ajustadas al presupuesto del usuario.

SCOPE busca facilitar la toma de decisiones para usuarios que desean mejorar el rendimiento de sus equipos sin necesidad de contar con conocimientos avanzados de hardware.

---

## Problema que resuelve

Muchos usuarios desconocen:

- Qué componentes tiene su computadora.
- Qué componente está limitando el rendimiento.
- Qué actualización conviene realizar primero.
- Cuánto deberían invertir.
- Qué producto podrían comprar.
- Cuándo deja de ser conveniente actualizar y es mejor cambiar de equipo.

SCOPE analiza estos factores y genera recomendaciones basadas en el hardware detectado y el presupuesto proporcionado.

---

## Arquitectura general

El funcionamiento principal del sistema es:

```text
Usuario
   |
   v
SCOPE Scanner
   |
   | Escaneo de hardware
   v
hardware.json
   |
   | Presupuesto
   v
upgrade_engine.py
   |
   +----------------------+
   |                      |
   v                      v
MongoDB Atlas        Análisis local
   |                      
   | Componentes
   | Equipos
   | Precios
   | Imágenes
   | Enlaces
   |
   v
Recomendaciones
   |
   v
resultados.json
   |
   v
SCOPE PWA
   |
   v
Dashboard de resultados
