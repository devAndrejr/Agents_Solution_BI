import streamlit as st
import base64
import io
import plotly.express as px

# Função para exportar gráficos
def get_image_download_link(fig, filename, text):
    """Gera um link para download da figura como imagem PNG"""
    try:
        # Tentar importar kaleido para verificar se está instalado
        import kaleido  # noqa: F401

        buf = io.BytesIO()
        fig.write_image(buf, format="png")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="{filename}.png">{text}</a>'
        return href
    except Exception as e:
        # Log the full exception for debugging
        st.error(f"Erro ao exportar gráfico como PNG: {e}")
        st.exception(e) # Display the full traceback in Streamlit

        # Alternativa quando kaleido não está disponível ou falha
        # Usar o formato HTML que não requer kaleido
        buf = io.StringIO()
        fig.write_html(buf)
        html_bytes = buf.getvalue().encode()
        b64 = base64.b64encode(html_bytes).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}.html">{text} (HTML)</a>'
        st.warning("Não foi possível exportar como PNG. Exportando como HTML. Verifique os logs para mais detalhes.")
        return href


# Função para exportar dados como CSV
def get_csv_download_link(df, filename, text):
    """Gera um link para download dos dados como CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">{text}</a>'
    return href


# Função para aplicar personalização ao gráfico
def apply_chart_customization(fig, chart_type, color_theme, show_grid, title_text):
    """Aplica personalizações ao gráfico Plotly"""
    # Aplicar tema de cores
    if color_theme == "Azul":
        color_sequence = px.colors.sequential.Blues
    elif color_theme == "Verde":
        color_sequence = px.colors.sequential.Greens
    elif color_theme == "Vermelho":
        color_sequence = px.colors.sequential.Reds
    elif color_theme == "Roxo":
        color_sequence = px.colors.sequential.Purples
    elif color_theme == "Arco-íris":
        color_sequence = px.colors.qualitative.Set1
    else:  # Padrão
        color_sequence = px.colors.qualitative.Plotly

    # Atualizar layout
    fig.update_layout(
        title=title_text,
        template="plotly_white" if show_grid else "plotly",
        colorway=color_sequence,
        margin=dict(l=40, r=40, t=50, b=40),
    )

    # Configurações específicas por tipo de gráfico
    if chart_type == "bar":
        fig.update_traces(marker_line_width=1, marker_line_color="#FFFFFF")
    elif chart_type == "pie":
        fig.update_traces(textinfo="percent+label", pull=[0.05, 0, 0, 0])

    return fig
