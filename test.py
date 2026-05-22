from pypdf import PdfReader

reader = PdfReader("plantilla_formulario.pdf")
fields = reader.get_fields()
print("Nombres detectados en tu PDF:")
for field_name in fields:
    print(f"- {field_name}")