import requests
from bs4 import BeautifulSoup
import psycopg2

# List of URLs where information about different crystals is located
urls = [
    "https://www.mindat.org/min-4322.html",
    "https://www.mindat.org/min-4341.html"
    # Add more URLs for the other crystals here
]

# Define a User-Agent header to mimic a web browser (you can change this)
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

# Create an empty list to store the extracted data for each crystal
all_crystals_data = []

# Iterate through each URL
for url in urls:
    # Set the User-Agent header in the request headers
    headers = {"User-Agent": user_agent}

    # Send an HTTP GET request to the URL with the User-Agent header
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the element with class "mineralheading" to get the crystal name
        crystal_name = soup.find("h1", class_="mineralheading").text

        # Find all image links for the crystal
        image_links = []
        image_elements = soup.find_all("img", width="288")  # Adjust the selector based on image location
        for img in image_elements:
            image_links.append(img["src"])

        # Find the element with id "introdata" (assuming the HTML structure is the same for all crystals)
        intro_data = soup.find("div", id="introdata")

        # Extract mineral information
        formula = intro_data.find("span", text="Formula:").find_next("div").text
        color = intro_data.find("span", text="Colour:").find_next("div").text
        lustre = intro_data.find("span", text="Lustre:").find_next("div").text
        hardness = intro_data.find("span", text="Hardness:").find_next("div").text
        specific_gravity = intro_data.find("span", text="Specific Gravity:").find_next("div").text
        crystal_system = intro_data.find("span", text="Crystal System:").find_next("div").text
        member_of = intro_data.find("span", text="Member of:").find_next("div").find("a").text
        name = intro_data.find("span", text="Name:").find_next("div").text

        # Create a dictionary to store the extracted data for this crystal
        crystal_data = {
            "Crystal Name": crystal_name,
            "Image Links": image_links,
            "Formula": formula,
            "Colour": color,
            "Lustre": lustre,
            "Hardness": hardness,
            "Specific Gravity": specific_gravity,
            "Crystal System": crystal_system,
            "Member of": member_of,
            "Name": name,
        }

        # Append the data for this crystal to the list
        all_crystals_data.append(crystal_data)
    else:
        print(f"Failed to retrieve data from URL: {url}")

# Database connection parameters
db_params = {
    "host": "localhost",  # Replace with your PostgreSQL server host
    "database": "Crystals",  # Replace with your database name
    "user": "postgres",  # Replace with your database username
    "password": "Quartz"  # Replace with your database password
}

try:
    conn = psycopg2.connect(**db_params)
except psycopg2.Error as e:
    print("Error connecting to the database:", e)
cursor = conn.cursor()

for crystal_data in all_crystals_data:
    sql = """
       INSERT INTO crystals (formula, colour, lustre, hardness, "specific gravity", "crystal system", "member of", name, "crystal name", "image links")
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    data = (
        crystal_data["Formula"],
        crystal_data["Colour"],
        crystal_data["Lustre"],
        crystal_data["Hardness"],
        crystal_data["Specific Gravity"],
        crystal_data["Crystal System"],
        crystal_data["Member of"],
        crystal_data["Name"],
        crystal_data["Crystal Name"],
        crystal_data["Image Links"]
    )
    cursor.execute(sql, data)

conn.commit()
cursor.close()
conn.close()
