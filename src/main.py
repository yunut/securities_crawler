import logging

import uvicorn
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware

from src.crawlers.pos_crawler import BasePosCrawler
# from src.crawlers.pos_crawler import crawl_new_pos
from src.entities.crawl_pos_result import CrawlNewPosResult

crawler = FastAPI()
crawler.add_middleware(CorrelationIdMiddleware)
logger = logging.getLogger(__name__)

@crawler.post("/crawl/pos",
              response_model=CrawlNewPosResult,
              response_model_exclude_unset=True,
              response_model_exclude_none=True
              )
async def crawl_pos_by_url():
    pos_crawler = BasePosCrawler()
    return pos_crawler.crawl_pos_schedule()


if __name__ == "__main__":
    uvicorn.run(crawler, host="0.0.0.0", port=8080, log_level="info")