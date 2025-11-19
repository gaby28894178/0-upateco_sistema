from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from svglib.svglib import svg2rlg


def _scaled_drawing(path: str, target_width_cm: float):
    d = svg2rlg(path)
    scale = (target_width_cm * cm) / float(d.width)
    d.scale(scale, scale)
    return d


def generate_srs_pdf(output_path: str):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=A4, title="SRS El Tata")
    story = []

    story.append(Paragraph('Sistema de Gestión de Pedidos "El Tata" — SRS (IEEE 830)', styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph('Resumen', styles['Heading2']))
    story.append(Paragraph('API REST funcionando para gestión de pedidos, productos y clientes. Basado en SRS IEEE 830 con imágenes y diagramas.', styles['BodyText']))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Endpoints', styles['Heading2']))
    story.append(Paragraph('Health, Productos CRUD, Clientes CRUD, Pedidos con estados y asignación de repartidor, Reportes de ventas.', styles['BodyText']))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Requisitos Funcionales', styles['Heading2']))
    story.append(Paragraph('RF-01 Registro de pedidos; RF-02 Estados; RF-03 Modificación limitada; RF-04 CRUD productos; RF-05 Cálculo totales; RF-06 Clientes; RF-07 Reportes.', styles['BodyText']))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Requisitos No Funcionales', styles['Heading2']))
    story.append(Paragraph('Usabilidad, rendimiento, seguridad, disponibilidad, escalabilidad, compatibilidad y backup.', styles['BodyText']))
    story.append(Spacer(1, 16))

    story.append(Paragraph('Diagramas', styles['Heading2']))
    story.append(Paragraph('Casos de uso', styles['Heading3']))
    story.append(_scaled_drawing('docs/images/casos_uso.svg', 16))
    story.append(Spacer(1, 12))
    story.append(Paragraph('Flujo de estados', styles['Heading3']))
    story.append(_scaled_drawing('docs/images/flujo_estados.svg', 16))
    story.append(Spacer(1, 16))

    story.append(Paragraph('Glosario', styles['Heading2']))
    story.append(Paragraph('Pedido, Ítem, Estado, Cliente, Producto.', styles['BodyText']))

    doc.build(story)