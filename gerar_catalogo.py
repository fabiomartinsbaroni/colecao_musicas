import os
import json
from pathlib import Path
from mutagen import File

# === CONFIGURAÇÃO: ALTERE PARA O CAMINHO DO SEU HD EXTERNO ===
PASTA_MUSICAS = "D:/"

EXTENSOES_VALIDAS = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma', '.alac'}

def formatar_tamanho(tamanho_bytes):
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if tamanho_bytes < 1024.0:
            return f"{tamanho_bytes:.1f} {unidade}"
        tamanho_bytes /= 1024.0
    return f"{tamanho_bytes:.1f} TB"

def obter_metadados(caminho_arquivo):
    ext = Path(caminho_arquivo).suffix.lower()
    tamanho = formatar_tamanho(os.path.getsize(caminho_arquivo))
    
    bitrate_str = "N/A"
    sample_rate_str = "N/A"
    duracao_str = "N/A"
    
    try:
        audio = File(caminho_arquivo)
        if audio is not None and hasattr(audio, 'info'):
            info = audio.info
            if hasattr(info, 'bitrate') and info.bitrate:
                bitrate_str = f"{int(info.bitrate / 1000)} kbps"
            if hasattr(info, 'sample_rate') and info.sample_rate:
                sample_rate_str = f"{info.sample_rate / 1000:.1f} kHz"
            if hasattr(info, 'length') and info.length:
                mins = int(info.length // 60)
                secs = int(info.length % 60)
                duracao_str = f"{mins}:{secs:02d}"
    except Exception:
        pass

    pasta_rel = os.path.relpath(os.path.dirname(caminho_arquivo), PASTA_MUSICAS)
    if pasta_rel == ".":
        pasta_rel = "Raiz"

    return {
        "nome": Path(caminho_arquivo).name,
        "pasta": pasta_rel,
        "ext": ext.replace('.', '').upper(),
        "tamanho": tamanho,
        "bitrate": bitrate_str,
        "sample_rate": sample_rate_str,
        "duracao": duracao_str
    }

def escanear_hd():
    lista_musicas = []
    if not os.path.exists(PASTA_MUSICAS):
        print(f"ERRO: A pasta '{PASTA_MUSICAS}' não foi encontrada. Verifique a letra do HD.")
        return []

    print(f"Escaneando '{PASTA_MUSICAS}'... Aguarde.")
    for raiz, _, arquivos in os.walk(PASTA_MUSICAS):
        for arq in arquivos:
            if Path(arq).suffix.lower() in EXTENSOES_VALIDAS:
                caminho_completo = os.path.join(raiz, arq)
                lista_musicas.append(obter_metadados(caminho_completo))
                
    print(f"Concluído! {len(lista_musicas)} músicas encontradas.")
    return lista_musicas

def gerar_html(musicas):
    dados_json = json.dumps(musicas, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Músicas</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background: #0f172a; color: #f8fafc; padding: 20px; }}
        .header {{ max-width: 1200px; margin: 0 auto 20px; text-align: center; }}
        h1 {{ margin-bottom: 8px; color: #38bdf8; }}
        .stats {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 15px; }}
        .search-box {{ width: 100%; max-width: 650px; padding: 12px 18px; font-size: 1rem; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #fff; outline: none; }}
        .search-box:focus {{ border-color: #38bdf8; }}
        .table-container {{ max-width: 1200px; margin: 0 auto; overflow-x: auto; background: #1e293b; border-radius: 8px; border: 1px solid #334155; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }}
        th, td {{ padding: 12px 16px; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #cbd5e1; font-weight: 600; position: sticky; top: 0; }}
        tr:hover {{ background: #334155; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; background: #0284c7; color: #fff; }}
        .badge-flac {{ background: #059669; }}
        .badge-wav {{ background: #d97706; }}
        .folder {{ color: #94a3b8; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Catálogo de Músicas</h1>
        <div class="stats">Exibindo <strong id="total-count">{len(musicas)}</strong> faixas</div>
        <input type="text" id="search" class="search-box" placeholder="Buscar por música, pasta, formato (FLAC, MP3) ou bitrate..." oninput="filtrar()">
    </div>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Arquivo</th>
                    <th>Pasta</th>
                    <th>Formato</th>
                    <th>Bitrate</th>
                    <th>Amostragem</th>
                    <th>Duração</th>
                    <th>Tamanho</th>
                </tr>
            </thead>
            <tbody id="tabela-corpo"></tbody>
        </table>
    </div>
    <script>
        const musicas = {dados_json};
        function renderTabela(lista) {{
            const corpo = document.getElementById('tabela-corpo');
            corpo.innerHTML = '';
            lista.forEach(m => {{
                let badgeClass = 'badge';
                if (m.ext === 'FLAC') badgeClass += ' badge-flac';
                if (m.ext === 'WAV') badgeClass += ' badge-wav';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${{m.nome}}</strong></td>
                    <td class="folder">${{m.pasta}}</td>
                    <td><span class="${{badgeClass}}">${{m.ext}}</span></td>
                    <td>${{m.bitrate}}</td>
                    <td>${{m.sample_rate}}</td>
                    <td>${{m.duracao}}</td>
                    <td>${{m.tamanho}}</td>
                `;
                corpo.appendChild(tr);
            }});
            document.getElementById('total-count').innerText = lista.length;
        }}
        function filtrar() {{
            const termo = document.getElementById('search').value.toLowerCase();
            const filtradas = musicas.filter(m => 
                m.nome.toLowerCase().includes(termo) ||
                m.pasta.toLowerCase().includes(termo) ||
                m.ext.toLowerCase().includes(termo) ||
                m.bitrate.toLowerCase().includes(termo)
            );
            renderTabela(filtradas);
        }}
        renderTabela(musicas);
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Arquivo 'index.html' gerado com sucesso!")

if __name__ == "__main__":
    lista = escanear_hd()
    if lista:
        gerar_html(lista)