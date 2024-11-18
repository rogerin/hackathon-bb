# Documentação do Projeto BBox

## Visão Geral do Projeto
O **BBox** é uma solução IoT desenvolvida durante um hackathon promovido pelo Banco do Brasil. O projeto consiste em uma **caixa inteligente** que utiliza **reconhecimento facial ou de objetos** para abertura, integrando tecnologias avançadas de visão computacional, comunicação IoT e microcontroladores para garantir segurança e eficiência.

---

## Arquitetura do Projeto
O projeto é composto pelos seguintes componentes principais:

### 1. **Lambda Functions na AWS**
#### a) Função: `BBoxConsult`
- **Descrição**: Consulta ao AWS Rekognition para validar o reconhecimento facial ou identificação de objetos.
- **Tecnologias Utilizadas**: Python, boto3.
- **Entrada**: Dados da imagem capturada pela câmera (em base64 ou link).
- **Saída**: Resultado da análise com um **status de validação** (autorizado ou não).
- **Endpoints**: Configurado na API Gateway da AWS.

#### b) Função: `BBoxAction`
- **Descrição**: Responsável por acionar o mecanismo de abertura da caixa com base nos resultados fornecidos pelo `BBoxConsult`.
- **Tecnologias Utilizadas**: Python, boto3.
- **Entrada**: Resultado da consulta (`authorized = true/false`).
- **Saída**: Comando enviado ao AWS IoT Core para controle do dispositivo físico.

---

### 2. **Microcontrolador ESP32 com MicroPython**
- **Finalidade**: Controlar o mecanismo físico da caixa.
- **Descrição**:
  - O ESP32 é programado em **MicroPython** para:
    - Conectar-se ao **broker MQTT** do AWS IoT Core.
    - Receber comandos de abertura ou fechamento da caixa.
    - Realizar o acionamento físico com base nos comandos recebidos.
- **Fluxo de Comunicação**:
  1. O ESP32 se conecta à rede Wi-Fi e ao broker MQTT do AWS.
  2. Subscrição aos tópicos relevantes para receber mensagens de controle.
  3. Interpretação das mensagens e acionamento dos relés ou motores para abrir/fechar a caixa.

---

### 3. **Página Web (HTML + CSS)**
- **Finalidade**: Interface simples para interação com o BBox, onde os usuários podem:
  - Capturar imagens para análise.
  - Verificar o status da caixa (aberta/fechada).
- **Recursos**:
  - Botão para enviar imagens para análise.
  - Indicadores visuais do status da caixa.
- **Estrutura Básica**:
  - HTML estático.
  - CSS para estilização.
  - Scripts em JavaScript para conexão via AJAX à API.

---

### 4. **N8N Workflow**
- **Descrição**: O **N8N** atua como um integrador que conecta o front-end da página com o MQTT Broker do AWS IoT Core.
- **Pipeline**:
  1. **Recepção**: Recebe as requisições da página web via webhook.
  2. **Processamento**: Chama as Lambdas necessárias (`BBoxConsult` e `BBoxAction`).
  3. **Comunicação**: Envia comandos para o MQTT do AWS IoT Core para operar a caixa.

---

### 5. **AWS IoT Core**
- **Finalidade**: Middleware de comunicação MQTT para controle da caixa física.
- **Fluxo**:
  - Recebe comandos via MQTT para abrir/fechar a caixa.
  - Retorna o status para o sistema.

---

## Tecnologias Utilizadas
- **AWS Services**:
  - Rekognition
  - Lambda
  - API Gateway
  - IoT Core
- **Microcontroladores**:
  - ESP32 com MicroPython
- **Front-End**:
  - HTML
  - CSS
  - JavaScript (AJAX)
- **Middleware**:
  - N8N
- **Linguagens de Programação**:
  - Python
  - MicroPython

---

## Funcionalidades
1. **Reconhecimento Facial/Objetos**:
   - Validação de usuários ou itens permitidos.
2. **Abertura Automatizada**:
   - Caixa abre apenas após validação bem-sucedida.
3. **Interface Web Simples**:
   - Captura e envio de imagens para análise.
   - Exibição do status da caixa.
4. **Integração com AWS IoT Core**:
   - Controle remoto em tempo real.
5. **Acionamento com ESP32**:
   - Controle do hardware físico conectado à caixa.

---

## Passos para Implementação

### 1. Configurar AWS Rekognition
- Criar um bucket no S3 para armazenar imagens temporárias.
- Configurar um modelo de reconhecimento no AWS Rekognition.

### 2. Criar as Lambdas
#### `BBoxConsult`
- Implementar lógica para consultar o Rekognition.
- Configurar permissões no IAM para acessar S3 e Rekognition.

#### `BBoxAction`
- Implementar lógica para publicar mensagens no MQTT.
- Configurar permissões no IAM para acessar o AWS IoT Core.

### 3. Configurar o Microcontrolador ESP32
- **Configurar Rede**: Conectar o ESP32 ao Wi-Fi local.
- **Subscrição MQTT**: Configurar subscrição aos tópicos do AWS IoT Core.
- **Acionamento**: Programar as ações físicas (abrir/fechar) com base nos comandos recebidos.

### 4. Configurar o N8N
- Criar um workflow que conecte:
  - Webhook para receber os dados do front-end.
  - Funções Lambda via HTTP Request.
  - AWS IoT Core via integração MQTT.

### 5. Desenvolver a Página Web
- Criar uma página estática com campos para upload de imagens.
- Adicionar scripts AJAX para comunicação com a API Gateway.

---

## Diagrama de Fluxo do Sistema

```plaintext
[Página Web]
     |
     v
  [N8N Workflow]
     |
  -----------------------
  |                    |
[Lambda: BBoxConsult] [Lambda: BBoxAction]
     |                    |
  [AWS Rekognition]      [AWS IoT Core]
                             |
                             v
                          [ESP32]
                             |
                             v
                        [Caixa Física]
```