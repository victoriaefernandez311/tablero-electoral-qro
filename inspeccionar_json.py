import json

archivos = [
    "mapas/secciones_2018.json",
    "mapas/secciones_2021.json",
    "mapas/secciones_2024.json"
]

for archivo in archivos:

    print("\n" + "="*60)
    print(archivo)
    print("="*60)

    with open(archivo, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\nTIPO:")
    print(type(data))

    if "features" in data:

        print("\nCANTIDAD FEATURES:")
        print(len(data["features"]))

        primera = data["features"][0]

        print("\nCLAVES FEATURE:")
        print(primera.keys())

        print("\nPROPERTIES:")
        print(primera["properties"].keys())

        print("\nPRIMERAS PROPERTIES:")
        print(primera["properties"])