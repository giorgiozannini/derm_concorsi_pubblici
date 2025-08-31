import requests
from bs4 import BeautifulSoup
import json
import os 
import time

n_attempts = 3
for attempt in range(n_attempts):
    print("Attempt n. ", attempt+1)

    try:
        url = "https://www.concorsipubblici.com/search?keys=dermatologia"
        page = requests.get(url)
        
        print("Response:", page.status_code)

        # Parse the HTML
        soup = BeautifulSoup(page.content, "html.parser")
        odd_rows = soup.find_all("div", {"class": "views-row odd"})
        even_rows = soup.find_all("div", {"class": "views-row even"})
        all_concorsi = odd_rows + even_rows


        with open('last_concorsi.json', 'r', encoding='utf-8') as f:
            last_concorsi = json.load(f)["ids"]

        if all_concorsi:
            
            ids = []
            for concorso in all_concorsi:

                id = str(concorso.find("article").get("data-history-node-id"))

                # Extract 'ente'
                ente = concorso.select_one("div.col-md-6 div.field__item")

                if ente and id not in last_concorsi:
                
                    ente_link = "https://www.concorsipubblici.com" + ente.find("a")["href"] if ente else None
                    ente_name = ente.find("a").get_text()

                    # Extract 'scadenza'
                    scadenza = concorso.select_one("div.col-md-4 div.field__item")
                    scadenza_date = scadenza.get_text().replace("\n", "").replace("Scaduto", "")

                    # Extract 'description'
                    description = concorso.select_one("div.contest-footer").get_text().strip().replace("\n", "")

                    concorsi_url = f"<a href='{url}'>pagina concorsi</a>"
                    ente_link = f"<a href='{ente_link}'>pagina ente</a>" if ente_link else "Pagina ente non trovata"

                    message = f"""
<b>Nuovo concorso di Dermatologia!!</b>

> <b>pagina</b>: {concorsi_url}
> <b>ente</b>: {ente_name}
> <b>link ente</b>: {ente_link}
> <b>descrizione</b>: {description}
> <b>scadenza</b>: {scadenza_date}
            """

                    token = os.getenv("TOKEN")
                    chat_id = os.getenv("CHAT_ID")

                    send_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={message}"
                    print(requests.get(send_url).json())
                    time.sleep(10)
                    
                ids.append(id)


            with open('last_concorsi.json', 'w', encoding='utf-8') as f:
                json.dump({"ids": ids}, f, indent=2, ensure_ascii=False)
                

    except Exception as e:
        print(e)
        print(ente_name, scadenza_date)
        time.sleep(10)
        continue

    else:
        break
