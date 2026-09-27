def chunk_text(text):
    text = text.replace("\r", "")

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    chunks = []
    current_chunk = []

    for line in lines:

        # Secțiuni noi
        if line in [
            "Laptopuri — 20 modele",
            "Telefoane — 15 modele"
        ]:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []

            current_chunk.append(line)
            continue

        # Un produs are 8 linii la laptop
        # și 7 linii la telefon.
        current_chunk.append(line)

        # Salvăm produsul când apare "În stoc"
        if line == "În stoc":
            chunks.append("\n".join(current_chunk))
            current_chunk = []

    # Salvăm informația rămasă
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks