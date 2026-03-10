# Chat seguro cliente-servidor com sockets TCP

## Descrição do projeto

Alunos envolvidos:
- Gabriel Craveiro de Oliveira Garcia
- Lucas Ferreira Silva
- Rafael Bruno Soares Gonçalves

Este projeto foi desenvolvido para a disciplina de Infraestrutura de Redes com o objetivo de implementar uma aplicação de chat utilizando o modelo cliente-servidor. A ideia principal foi colocar em prática conceitos estudados durante a disciplina, como comunicação em rede com sockets, protocolos de transporte, criptografia de dados e organização de aplicações distribuídas.

O sistema consiste em um servidor central que aceita conexões de múltiplos clientes ao mesmo tempo. Cada cliente pode se autenticar com um usuário e senha, enviar mensagens para o servidor e receber mensagens enviadas por outros usuários conectados.

As mensagens não são transmitidas em texto puro. Antes de serem enviadas pela rede, elas passam por um processo de serialização e criptografia, garantindo que os dados trafeguem protegidos entre cliente e servidor.

Além da parte de comunicação em rede, o cliente possui uma interface gráfica simples desenvolvida com Tkinter, permitindo que o usuário interaja com o chat de forma mais intuitiva.

---

## Linguagem utilizada

O projeto foi desenvolvido utilizando **Python**.

Foram utilizadas principalmente bibliotecas da própria linguagem, além de uma biblioteca externa para criptografia.

Bibliotecas utilizadas:

- socket — responsável pela comunicação em rede
- threading — utilizada para permitir múltiplos clientes conectados ao mesmo tempo
- tkinter — utilizada para criar a interface gráfica do cliente
- json — utilizada para serialização das mensagens
- cryptography — utilizada para implementar a criptografia das mensagens

---

## Como executar o projeto

Antes de executar o projeto, é necessário instalar a biblioteca utilizada para criptografia.

### 1. Instalar dependência

Abra o terminal na pasta do projeto e execute:

pip install cryptography

### 2. Iniciar o servidor

Ainda na pasta principal do projeto, execute o seguinte comando:

python -m servidor.servidor_chat

Se o servidor iniciar corretamente, o terminal mostrará uma mensagem indicando que ele está aguardando conexões.

### 3. Iniciar o cliente

Em outro terminal, também na pasta do projeto, execute:

python -m cliente.cliente_chat

Ao executar o cliente, será aberta uma janela solicitando usuário e senha. Após autenticação, a interface do chat será exibida.

### 4. Abrir mais clientes

Para testar o funcionamento do chat entre vários usuários, basta abrir novos terminais e executar novamente:

python -m cliente.cliente_chat

Cada cliente conectado poderá enviar e receber mensagens em tempo real.

---

## Usuários disponíveis para teste

Os usuários cadastrados estão definidos no arquivo:

dados/usuarios.json

Alguns usuários disponíveis para teste:

- usuário: gabriel | senha: 1234
- usuário: admin | senha: admin
- usuário: thiago | senha: thiago123

---

## Explicação da criptografia utilizada

Para proteger as mensagens transmitidas pela rede, foi utilizada **criptografia simétrica**. Nesse tipo de criptografia, tanto o cliente quanto o servidor utilizam a mesma chave para criptografar e descriptografar os dados.

Neste projeto foi utilizada a biblioteca **cryptography**, mais especificamente o mecanismo **Fernet**, que internamente utiliza criptografia baseada em AES.

Antes de serem enviadas pela rede, as mensagens passam pelas seguintes etapas:

1. A mensagem é transformada em um objeto JSON.
2. Esse JSON é convertido para bytes.
3. Os bytes são criptografados usando a chave compartilhada.
4. O pacote criptografado é enviado pelo socket.

Quando o servidor recebe a mensagem, o processo é invertido:

1. O pacote criptografado é recebido.
2. Os dados são descriptografados utilizando a mesma chave.
3. O conteúdo é convertido novamente de bytes para JSON.
4. O servidor interpreta a mensagem e a retransmite para os outros clientes.

A chave utilizada no projeto é derivada de uma frase secreta definida no código. Essa frase passa por um processo de hash utilizando SHA-256 e depois é convertida para o formato exigido pelo Fernet. Dessa forma, tanto cliente quanto servidor conseguem gerar a mesma chave sem precisar transmiti-la pela rede.

---

## Arquitetura da solução

A aplicação segue o modelo clássico de **arquitetura cliente-servidor**.

### Servidor

O servidor é responsável por:

- escutar conexões TCP em uma porta definida
- aceitar múltiplos clientes simultaneamente
- autenticar usuários com base no arquivo de dados
- receber mensagens enviadas pelos clientes
- descriptografar as mensagens recebidas
- retransmitir as mensagens para os outros clientes conectados

Para lidar com vários clientes ao mesmo tempo, o servidor utiliza **threads**, criando uma nova thread para cada conexão estabelecida.

### Cliente

O cliente é responsável por:

- conectar ao servidor utilizando sockets TCP
- enviar as credenciais de login
- abrir a interface gráfica do chat após autenticação
- enviar mensagens digitadas pelo usuário
- receber mensagens retransmitidas pelo servidor

A interface do cliente foi desenvolvida utilizando **Tkinter**, permitindo interação simples com o sistema.

### Comunicação entre cliente e servidor

A comunicação ocorre utilizando **sockets TCP**, que garantem entrega confiável das mensagens.

Cada mensagem enviada é organizada em um pacote contendo:

- tipo da mensagem (login, mensagem ou saída)
- conteúdo da mensagem
- dados adicionais quando necessário

Esses dados são serializados em JSON, criptografados e enviados pelo socket. Ao receber o pacote, o destinatário realiza o processo inverso para recuperar as informações originais.

---

## Organização do projeto

A estrutura do projeto foi organizada em pastas para separar responsabilidades:

- cliente/ → código da aplicação cliente
- servidor/ → código responsável por gerenciar conexões
- seguranca/ → funções relacionadas à criptografia
- comum/ → protocolo de envio e recebimento de pacotes
- dados/ → armazenamento dos usuários cadastrados

Essa organização facilita a manutenção do código e deixa o projeto mais claro para quem for analisar ou continuar o desenvolvimento.

---

## Considerações finais

O protocolo escolhido para comunicação foi o **TCP**, pois ele garante maior confiabilidade na entrega das mensagens, controle de fluxo e ordenação correta dos pacotes.

O projeto demonstra na prática a implementação de um sistema cliente-servidor simples, utilizando conceitos fundamentais de redes de computadores, segurança da informação e programação concorrente.

Apesar de ser uma aplicação simples, ela mostra de forma clara como sistemas distribuídos podem se comunicar de forma segura utilizando sockets e criptografia.
