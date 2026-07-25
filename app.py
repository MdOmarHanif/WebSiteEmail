import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="Website Email Finder", page_icon="📧")

st.title("📧 Website Email Finder")
st.markdown("### MD Omar Hanif")

website = st.text_input("Website URL")


def extract_emails(text):
    return set(re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
        re.IGNORECASE
    ))


headers = {
    "User-Agent": "Mozilla/5.0"
}


if st.button("Email Finder"):

    if not website:
        st.warning("Please enter a website.")
        st.stop()

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    emails = set()
    visited = set()

    keywords = [
        "contact",
        "about",
        "support",
        "help",
        "team",
        "company",
        "privacy",
        "terms",
        "legal"
    ]

    try:

        with st.spinner("Searching..."):

            response = requests.get(
                website,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            visited.add(website)

            html = response.text

            emails.update(extract_emails(html))

            soup = BeautifulSoup(html, "html.parser")

            pages = []

            for link in soup.find_all("a", href=True):

                href = urljoin(website, link["href"])

                if href in visited:
                    continue

                if any(word in href.lower() for word in keywords):
                    pages.append(href)

            for page in pages:

                try:

                    r = requests.get(
                        page,
                        headers=headers,
                        timeout=15
                    )

                    if r.status_code == 200:
                        visited.add(page)
                        emails.update(extract_emails(r.text))

                except:
                    pass

        if emails:

            st.success(f"Found {len(emails)} email(s)")

            for email in sorted(emails):
                st.write(email)

        else:

            st.info("No email addresses found.")

    except Exception as e:

        st.error(f"Error: {e}")
