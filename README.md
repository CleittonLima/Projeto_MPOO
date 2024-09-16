# Projeto MPOO

OBS: não é necessário adicionar o ID, pois ele gera automaticamente, se colocar um ID ele sempre será por ordem.
Primeiro criado: ID = 1

### Projeto desenvolvido em grupo
Erisvaldo Cleiton de Almeida Lima

Igor Enrique Pereira de Lima

Elielson Vincente de Souza

# Sistema de Registro de Hotel

Este projeto implementa um sistema básico de gestão de hotel utilizando FastAPI, uma estrutura web moderna e de alta performance para a criação de APIs em Python. O sistema permite a gestão de quartos, clientes, reservas, itens e compras em um hotel, utilizando arquivos JSON para armazenamento de dados.

## Funcionalidades
- **Gestão de Quartos**: Adicionar, editar, remover e listar quartos disponíveis no hotel.

- **Gestão de Clientes**: Registrar novos clientes no sistema e gerenciar informações de clientes existentes.

- **Gestão de Reservas**: Realizar e cancelar reservas de quartos, garantindo a verificação da existência do cliente e do quarto antes da confirmação.

- **Gestão de Itens**: Adicionar itens que podem ser comprados pelos clientes durante a estadia.

- **Gestão de Compras**: Registrar compras de itens feitas pelos clientes, associando-as ao cliente correspondente.

- **Visualização de Dados**: Endpoint para exibir todos os dados armazenados no sistema, incluindo quartos, clientes, reservas, itens e compras.

## Como Usar

Instale o FastAPI, Uvicorn e o Pydantic para que funcione

Copiar código para instalar

    ```bash
    pip install fastapi uvicorn pydantic
    ```


Executar o Servidor: Inicie o servidor FastAPI usando Uvicorn:

Copiar código e execulte no terminal

    ```bash
    uvicorn hotelpart1:app --reload
    ```

O servidor será iniciado e poderá ser acessado em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Endpoints Principais
- **POST** `/quartos/` - Adicionar um novo quarto

- **PUT** `/quartos/{quarto_id}` - Editar um quarto existente

- **DELETE** `/quartos/{quarto_id}` - Remover um quarto

- **POST** `/clientes/` - Registrar um novo cliente

- **POST** `/reservas/` - Fazer uma nova reserva

- **DELETE** `/reservas/{reserva_id}` - Cancelar uma reserva

- **POST** `/itens/` - Adicionar um novo item disponível para compra

- **POST** `/compras/` - Registrar a compra de um item por um cliente

- **GET** `/dados_hotel/` - Exibir todos os dados do hotel

## Estrutura de Dados

Os dados são armazenados localmente em arquivos JSON:

- `quartos.json`

- `clientes.json`

- `reservas.json`

- `itens.json`

- `compras.json`

Cada arquivo armazena os registros correspondentes a sua entidade, permitindo persistência de dados entre execuções do servidor.
