import scrapy
import json
from geopy.geocoders import Nominatim
import csv

class QuotesSpider(scrapy.Spider):
    name = "shephora"

    def __init__(self):
        tsvfile = open('records.tsv', 'w')
        self.tsvwriter = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
        self.tsvwriter.writerow(["store_name", "store_number", "address", "address2", "city", "state", "zip_code", "country",
               "phone_number", "latitude", "longitude", "store_hours", "store_type", "other_fields"])

    def start_requests(self):
        yield scrapy.Request(url='http://www.sephora.com/storelist', callback=self.get_store_list)
        
    # get list of all stores in store list page
    def get_store_list(self, response):
        # crawl list of countries
        countries = response.xpath("//div[@class='u-py4']")
        for country in countries:
            country_name = country.xpath(".//h1/text()").extract_first().strip()

            # crawl list of states
            states = country.xpath(".//div[@class='StoresByState-item u-pb4']")
            for state in states:
                state_name = state.xpath(".//h2/text()").extract_first().strip()

                # crawl list of stores
                stores = state.xpath(".//ul//li")
                for store in stores:
                    store_link = store.xpath(".//a/@href").extract_first().strip()
                    store_name = store.xpath(".//a/text()").extract_first().strip()

                    request = scrapy.Request(url=store_link, callback=self.parse_store)
                    request.meta["country"] = country_name
                    request.meta["state"] = state_name
                    request.meta["store_name"] = store_name
                    yield request

    # get store info in store detail page
    def parse_store(self, response):
        info = response.xpath("//script[@type='application/ld+json']/text()").extract_first().strip()
        info_json = json.loads(info)
        address = info_json["address"]

        store = dict()
        store = {"name": response.meta["store_name"], "address": address["streetAddress"], 
                    # "address2": "%s, %s %s" % (address["addressLocality"], address["addressRegion"], address["postalCode"]), 
                    "city": address["addressLocality"],
                    "state": response.meta["state"], "zip_code": address["postalCode"], 
                    "country": response.meta["country"], "phone_number": address["telephone"],
                    "store_type": info_json["@type"], "store_hours": "; ".join(info_json["openingHours"])}

        try:
            geolocator = Nominatim()
            location = geolocator.geocode("%s %s" % (store["address"], store["address2"]))
            store["latitude"], store["longitude"] = location.latitude, location.longitude
        except:
            store["latitude"], store["longitude"] = "", ""

        try:
            store["address2"] = response.xpath("//li[@class='store-address2']/text()").extract()[0].strip()
        except:
            store["address2"] = ""
        
        self.save_store(store)
        # print json.dumps(info_json, indent=4)

    # save store info in tsv file
    def save_store(self, store):
        temp = [store["name"], "", store["address"], store["address2"], store["city"], store["state"], 
                  store["zip_code"], store["country"], store["phone_number"], store["latitude"], store["longitude"],
                  store["store_hours"], store["store_type"], ""]
        self.tsvwriter.writerow(temp)

