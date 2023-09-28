BOT_NAME = "prendas"

SPIDER_MODULES = ["prendas.spiders"]
NEWSPIDER_MODULE = "prendas.spiders"

ROBOTSTXT_OBEY = True

#CONCURRENT_REQUESTS = 15

DOWNLOAD_DELAY = 1

DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

COOKIES_ENABLED = True

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0"

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "DNT": "1",
    "Cache-Control": "no-cache",
}

ITEM_PIPELINES = {
    "prendas.pipelines.erroneos.PipelineErroneos": 200,
    "prendas.pipelines.ninos.PipelineNinos": 300,
    "prendas.pipelines.limpieza.PipelineLimpieza": 400,
    "prendas.pipelines.imagenes.PipelineImagenes": 500,
    "prendas.pipelines.basedatos.PipelineBaseDatos": 600
}

DOWNLOADER_MIDDLEWARES={
    "prendas.middlewares.errorhttp.ErrorHttpDownloaderMiddleware": 500,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

FEED_EXPORT_ENCODING = "utf-8"

RETRY_ENABLED = True
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 20


LOG_LEVEL = 'WARNING'
LOG_FILE = './logs/prendas.log'

IMAGES_URLS_FIELD = 'url_imagen'
IMAGES_RESULT_FIELD = 'ruta_imagen'
MEDIA_ALLOW_REDIRECTS = True
IMAGES_EXPIRES = 90
IMAGES_THUMBS = {
   "miniaturas": (302, 453),
}
