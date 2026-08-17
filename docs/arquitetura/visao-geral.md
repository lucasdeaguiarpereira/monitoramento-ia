# Arquitetura oficial

Este documento define a arquitetura oficial do **Monitoramento IA**. Alterações na
organização dos módulos exigem uma justificativa arquitetural forte e devem ser
registradas em `docs/decisoes/`.

## Princípios

- Organização por responsabilidade de domínio, não por tecnologia.
- Simplicidade, legibilidade, baixo acoplamento e facilidade de evolução.
- Python restrito ao módulo `vision`.
- Laravel responsável pelo domínio da aplicação, sem processamento de imagem.
- Vue responsável exclusivamente pela interface do usuário.
- `vision` deve funcionar independentemente de `backend` e `frontend`.
- `backend` nunca deve depender de OpenCV, YOLO ou bibliotecas de visão computacional.
- `vision` deve poder ser substituído por outra implementação sem afetar os demais módulos.

## Fluxo

```text
Câmera
  -> Capture
  -> AI
  -> Events
  -> Services
  -> Backend (Laravel)
  -> Frontend (Vue)
```

## Responsabilidades

### `vision/capture`

Comunicação com dispositivos físicos: RTSP, ONVIF, descoberta de câmeras,
gerenciamento de streams e conexão. Não contém regras de negócio.

### `vision/ai`

Visão computacional: detecção, rastreamento, reconhecimento facial, OCR e leitura
de placas. Toda IA permanece isolada neste módulo.

### `vision/events`

Transforma resultados da IA em eventos de negócio. Não executa IA.

### `vision/services`

Integrações externas, como API do Laravel, FTP, MQTT, armazenamento, filas, Redis
e RabbitMQ.

### `backend`

Domínio e regras de negócio da aplicação. Não processa imagens.

### `frontend`

Interface do usuário.

## Primeiro marco

O primeiro marco técnico é conectar ao stream RTSP e capturar um único frame com
Python. Nenhuma funcionalidade de IA faz parte desse marco.

