import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de ejemplo para scraping
url = "https://www.bodas.net/wedding-planners/malaga"

# Realiza la solicitud de la página
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

# Encuentra los elementos que contienen la información relevante
planners = soup.find_all('div', class_='provider-card')

# Extrae la información
data = []
for planner in planners:
    name = planner.find('h3', class_='title').text.strip()
    website = planner.find('a', class_='web')['href'] if planner.find('a', class_='web') else None
    email = "Obtener manualmente"
    
    data.append({'Nombre': name, 'Website': website, 'Correo': email})

# Convierte a un DataFrame de Pandas
df = pd.DataFrame(data)
# Muestra los resultados
df.head()