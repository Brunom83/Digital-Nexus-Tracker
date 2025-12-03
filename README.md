# 🦖 Digital Nexus Tracker (DMO)

Uma aplicação desktop moderna para gestão de progresso no servidor privado *Digital Nexus Online* (DMO).
Desenvolvido em **Python** com **PySide6** (Qt) e **SQLite**.

![Screenshot da App](https://via.placeholder.com/800x450?text=Coloca+aqui+um+Print+do+Dashboard) 
*(Dica: Tira um print do Dashboard e mete na pasta do projeto, depois linka aqui!)*

## 🚀 Funcionalidades

* **📊 Dashboard Financeiro:** Monitoriza pontos (Easy, Normal, Hard) e calcula o progresso para o próximo nível VIP.
* **🛒 Gestão de Lojas:** Adiciona itens das lojas do jogo manualmente, com imagens e preços dinâmicos.
* **📋 Coleção & Seals:** Importa e gere a tua checklist de Digimons e Selos (AT, HP, DE, etc.).
* **⚔️ Dungeon Tracker:** Regista as tuas runs e histórico de ganhos.
* **🧮 Calculadora de Grind:** Descobre exatamente quantas runs precisas para comprar aquele item de 30k pontos.
* **💾 Sistema de Perfis:** Suporte para múltiplos utilizadores (Login Local).

## 🛠️ Instalação (Para Developers)

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Brunom83/Digital-Nexus-Tracker.git](https://github.com/Brunom83/Digital-Nexus-Tracker.git)
    cd Digital-Nexus-Tracker
    ```

2.  **Crie um ambiente virtual (Recomendado):**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    python src/app.py
    ```

## 📦 Como criar o Executável (.exe)

Para compilar a aplicação para Windows:

```bash
pip install pyinstaller
pyinstaller --noconsole --onedir --name="DMOTracker" --add-data "data;data" src/app.py