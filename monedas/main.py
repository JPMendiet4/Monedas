import threading
import scrapy
from fastapi import FastAPI
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import uvicorn

app = FastAPI()

# Variable para almacenar los datos obtenidos por la araña
scraped_data = []


class GoogleFinanceSpider(scrapy.Spider):
    name = 'googlefinance'
    start_urls = [
        'https://www.google.com/finance/quote/USD-PEN?sa=X&ved=2ahUKEwid-a6B8KGFAxWKRTABHexdDn8QmY0JegQIBhAo',
        'https://www.google.com/finance/quote/EUR-PEN?sa=X&ved=2ahUKEwieudaz8KGFAxWbSDABHecRCOAQmY0JegQIBhAo'
    ]

    def parse(self, response):
        value = response.css('div.YMlKec.fxKbKc::text').get()

        if 'USD-PEN' in response.url:
            currency = 'DOLARES'
        elif 'EUR-PEN' in response.url:
            currency = 'EUROS'

        data = {
            currency: float(value)
        }

        # Almacena los datos en la lista scraped_data
        scraped_data.append(data)


def run_crawler():
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    })
    process.crawl(GoogleFinanceSpider)
    process.start()


@app.on_event("startup")
async def startup_event():
    # Iniciar el proceso de scraping en un hilo
    threading.Thread(target=run_crawler).start()


@app.get("/")
async def get_scraped_data():
    # Devuelve los datos obtenidos por la araña
    return scraped_data


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
