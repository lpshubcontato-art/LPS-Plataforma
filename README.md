# Plataforma LPS - Liderança Psicanalítica

Plataforma de desenvolvimento de liderança baseada em conceitos psicanalíticos, desenvolvida por Viviane Nishiura.

## Arquivo Principal

O arquivo principal da aplicação é `main.py`.

## Como Executar

```bash
streamlit run main.py --server.port 5000
```

## Configuração no Streamlit Cloud

Ao hospedar no Streamlit Cloud, configure as seguintes variáveis em **Settings > Secrets**:

```toml
OPENAI_API_KEY = "sua-chave-aqui"
```

## Funcionalidades

- Curso de Liderança Psicanalítica (7 módulos)
- LPSTest - Assessment de perfil de liderança (48 questões)
- Gestão de Equipe - Links para até 4 funcionários
- LPSChat - Consultor de IA com contexto da equipe
- Mentoria - Agendamento via WhatsApp
