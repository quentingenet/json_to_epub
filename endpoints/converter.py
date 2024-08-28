from models.jsoninput import JSONInput
from fastapi import APIRouter, HTTPException
from ebooklib import epub
import requests


router = APIRouter()

def parse_json_to_epub_content(json_data, level=1):
    content = ""
    for key, value in json_data.items():
        if isinstance(value, dict):
            content += f"<h{level}>{key}</h{level}>"
            content += parse_json_to_epub_content(value, level + 1)
        elif isinstance(value, list):
            content += f"<h{level}>{key}</h{level}><ul>"
            for item in value:
                content += f"<li>{parse_json_to_epub_content(item, level + 1) if isinstance(item, dict) else item}</li>"
            content += "</ul>"
        else:
            content += f"<p><strong>{key}:</strong> {value}</p>"
    return content

@router.post("/convert/")
async def convert_json_to_epub(input_data: JSONInput):
    try:
        # Créer le livre EPUB
        book = epub.EpubBook()
        book.set_title("Generated Book")
        book.set_author("API Author")

        # Générer un chapitre principal avec tout le contenu du JSON
        chap = epub.EpubHtml(title="Main Chapter", file_name='chap_1.xhtml', lang='en')
        chap.content = parse_json_to_epub_content(input_data.json_to_convert)
        book.add_item(chap)
        book.toc.append(epub.Link(chap.file_name, chap.title, chap.title))

        # Ajouter les éléments par défaut NCX et NAV
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Style CSS simple
        style = 'body { font-family: Arial, sans-serif; }'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # Écrire le fichier EPUB
        output_filename = "generated_book.epub"
        epub.write_epub(output_filename, book)

        # Envoyer le fichier EPUB au endpoint fourni
        with open(output_filename, 'rb') as f:
            response = requests.post(input_data.return_endpoint, files={"file": f})

        if response.status_code == 200:
            return {"message": "EPUB created and sent successfully"}
        else:
            return {"message": "EPUB created, but failed to send", "status_code": response.status_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
