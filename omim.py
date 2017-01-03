#!/usr/bin/env python
#coding=utf-8

import re
import scrapy

class omimSpider(scrapy.Spider):
    name = 'omim'
    custom_settings = {
        'USER_AGENT':'bingbot',
        'BOT_NAME':'bingbot',
        'COOKIES_ENABLED':False,
        'DOWNLOAD_DELAY':4
    }


    def __init__(self, filename=None):
        URL_BASE = 'https://www.omim.org/entry/'
        if filename:
            with open(filename, 'r') as f:
                omim_ids = [re.findall(r'\((\d+)\)', line )  for line in f if line.startswith('chr') ]
                self.start_urls = [ '{0}{1}'.format(URL_BASE, int(omim[0]) ) for omim in omim_ids if omim]
#                 self.start_urls = ['https://www.omim.org/entry/131244']
    def parse(self, response):
        gene_pheno = {}
        gene_pheno['url'] = response.url
        gene_pheno['omim_num'] = re.findall(r'(\d+)',response.url)[0]
        #extract from Description
        if 'Description' in response.text:
            gene_pheno['description'] = ','.join(response.xpath('//div[@id="descriptionFold"]/span/p/text()').extract() )
        #extract from table
        if response.xpath('//table'):
            tr = response.xpath('//table/tbody/tr') #maybe one or more trs

            gene_pheno['location'] = tr[0].xpath('td')[0].xpath('span/a/text()').extract_first().strip() #first td of first tr in table
            phenotype = tr[0].xpath('td')[1].xpath('span/text()').extract_first().strip()
            mim = tr[0].xpath('td')[2].xpath('span/a/text()').extract_first()
            inherit = ','.join(tr[0].xpath('td')[3].xpath('span/abbr/text()').extract() )
            pheno_key = tr[0].xpath('td')[4].xpath('span/abbr/text()').extract_first()
            
            gene_pheno[mim] = [phenotype, inherit, pheno_key]
            
            if len(tr) > 1:
                for tb_record in tr[1:]: #less num of column than the tr above
                    phenotype = tb_record.xpath('td')[0].xpath('span/text()').extract_first().strip()
                    min = tb_record.xpath('td')[1].xpath('span/a/text()').extract_first()
                    inherit = ','.join(tb_record.xpath('td')[2].xpath('span/abbr/text()').extract() )
                    pheno_key = tb_record.xpath('td')[3].xpath('span/abbr/text()').extract_first()
                    gene_pheno[mim] = [phenotype, inherit, pheno_key]
        return gene_pheno


