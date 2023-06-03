import sys
import subprocess
import requests
import openai
from bs4 import BeautifulSoup
import contextlib
import os

# Function to disable scraping output
@contextlib.contextmanager
def disable_scraping_output():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# Function to install a Python package
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Installation failed. Error: {str(e)}")
        if e.output is not None:
            print(f"Output: {e.output.decode()}")

# Check if 'requests' package is installed, if not, install it
try:
    import requests
except ImportError:
    print("'requests' package not found. Installing...")
    install_package('requests')
    import requests

# Check if 'openai' package is installed, if not, install it
try:
    import openai
except ImportError:
    print("'openai' package not found. Installing...")
    install_package('openai')
    import openai

# Check if 'beautifulsoup4' package is installed, if not, install it
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("'beautifulsoup4' package not found. Installing...")
    install_package('beautifulsoup4')
    from bs4 import BeautifulSoup

# Prompt the user to enter their OpenAI API key
api_key = input("Enter your OpenAI API key: ")
openai.api_key = api_key

# Function to scrape news data from the GB News website
def scrape_gbnews():
    url = 'https://www.gbnews.uk/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='MuiCard-root MuiPaper-root jss491 MuiPaper-elevation1 MuiCard-elevation0 MuiPaper-rounded')

    news_data = []
    for article in articles:
        try:
            title = article.find('h2', class_='MuiTypography-root jss452 MuiTypography-h4 MuiTypography-gutterBottom').text.strip()
            summary = article.find('p', class_='MuiTypography-root jss460 MuiTypography-body1').text.strip()

            news_data.append({
                'title': title,
                'summary': summary
            })
        except AttributeError:
            # Handle case when desired element is not found
            continue

    return news_data

# Function to scrape news data from the BBC News website
def scrape_bbcnews():
    url = 'https://www.bbc.co.uk/news'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='gs-c-promo')
    
    news_data = []
    for article in articles:
        try:
            title = article.find('h3', class_='gs-c-promo-heading__title').text.strip()
            summary = article.find('p', class_='gs-c-promo-summary').text.strip()

            news_data.append({
                'title': title,
                'summary': summary
            })
        except AttributeError:
            # Handle case when desired element is not found
            continue

    return news_data

# Function to interact with the OpenAI model and generate a response
def get_model_response(prompt):
    try:
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            temperature=0.7,
            max_tokens=100,
            n=1,
            stop=None,
            timeout=10
        )
        return response.choices[0].text.strip()
    except openai.OpenAIError as e:
        print(f"Error generating AI response: {str(e)}")
        return None

# Main game loop
while True:
    with disable_scraping_output():
        # Scrape news data from GB News
        news_data = scrape_gbnews()

        # If no news data is available from GB News, scrape from BBC News as a backup source
        if not news_data:
            news_data = scrape_bbcnews()

    # Extract and condense news summary
    condensed_summary = "\n".join(article['summary'] for article in news_data if article['summary'])

    # Print the condensed news summary
    print("\nCondensed News Summary:")
    if condensed_summary:
        print(f"In the UK, there is\n{condensed_summary}")
    else:
        print("No news data available.")

    # User prompt
    user_prompt = input("\nWhat will you do? ")

    # Generate AI response
    prompt = f"In the UK, there is\n{condensed_summary}\nUser Action: {user_prompt}"
    ai_response = get_model_response(prompt)

    # Print the AI-generated response
    if ai_response:
        print("\nAI Response:")
        print(ai_response)

    # Ask the user to play again or exit
    play_again = input("\nDo you want to play again? (yes/no): ")
    if play_again.lower() != 'yes':
        break

print("\nThank you for playing the game!")
