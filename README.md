# :books: The Book Is Right :books:

The Book Is Right is a serverless implementation of a web scraper for book prices, based on Python 3.

### Why?

Everyone loves to get the best bang for their buck. And books are no exception, whether it is for college or just for personal pleasure!

This started as a personal project to get my college books for the best price possible, as they get quite expensive. 
It was built from the beginning to run in a serverless cloud environment.

## Requirements
* An AWS account
    * AWS Access Key ID
    * AWS Secret Access Key
    * Preferred region to deploy
* SMTP server to send e-mails (I've used AWS SES, but any Gmail or Outlook account is fine)
* Python 3.6+ installed

## Installation
To install "The Book Is Right" you just have to run the following commands:

1. Create a virtual environment (venv) inside the root folder of the project.
    ```bash
    python3 -m venv venv
    ```
2. Source the newly created virtual environment.
    ```bash
    source venv/bin/activate
    ```
3. Install all the "pip" packages from `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
4. Fill out the variables inside the `settings.py` file.
5. Run the CLI app to auto-deploy it to AWS.
    ```bash
    python thebookisright.py deploy
    ```
6. Done!

## What bookstores are currently available?
:globe_with_meridians:  
Book Depository - https://www.bookdepository.com/

:fr:  
Amazon France - https://www.amazon.fr/

:de:  
Amazon Deutschland - https://www.amazon.de/

:it:  
Amazon Italia - https://www.amazon.it/

:portugal:  
Almedina - https://www.almedina.net/  
Bertrand - https://www.bertrand.pt/  
FCA - https://www.fca.pt/  
Wook - https://www.wook.pt/

:es:  
Amazon España - https://www.amazon.es/

:uk:  
Amazon UK - https://www.amazon.co.uk/

This scraper is very focused on Europe, but you're free to contribute with your favourite bookstores! Just make a pull request with your bookstore and I'll be more than happy to include it in this repository.