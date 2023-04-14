import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

url = "https://myip.ms/browse/sites/208/own/376714/cntVisitors/300/cntVisitorsii/3000"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table", {"id": "sites_tbl"})

data = {"Domain": [], "Email": []}

for row in table.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) < 2:
        continue
    domain = cols[1].text.strip()
    data["Domain"].append(domain)

    print(f"Scanning {domain}...")
    try:
        domain_response = requests.get(f"http://{domain}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        data["Email"].append("")
        continue
    domain_soup = BeautifulSoup(domain_response.text, "html.parser")

    # Look for email on page
    email_regex = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"
    emails = set(re.findall(email_regex, domain_response.text))
    if emails:
        email = ", ".join(emails)
        data["Email"].append(email)
        print(f"Emails found on {domain} homepage: {email}")
        continue

    # Look for contact page link
    contact_link = None
    for link in domain_soup.find_all('a'):
        href = link.get('href')
        if href and 'contact' in href.lower():
            contact_link = href
            break

    # If contact link not found, move to next domain
    if not contact_link:
        print(f"No contact page found on {domain}")
        data["Email"].append("")
        continue

    # Check contact page for email
    try:
        contact_response = requests.get(contact_link)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        data["Email"].append("")
        continue
    contact_soup = BeautifulSoup(contact_response.text, "html.parser")
    emails = set(re.findall(email_regex, contact_response.text))
    if emails:
        email = ", ".join(emails)
        data["Email"].append(email)
        print(f"Emails found on {domain} contact page: {email}")
    else:
        print(f"No emails found on {domain} contact page")
        data["Email"].append("")

# Check that all arrays are of the same length
if not all(len(x) == len(data["Domain"]) for x in data.values()):
    raise ValueError("All arrays in 'data' must be of the same length")

df = pd.DataFrame(data)
df.to_excel("email_results3.xlsx", index=False)
print(df)
