import scrapy
class cadSpider(scrapy.Spider):
    name = 'cad'
    allowed_domains = 'bioguo.org'
    start_urls = [
        'http://www.bioguo.org/CADgene/browseAllSNP.php'
    ]
    def parse(self, response):
        for tr in response.xpath('//tr')[4:-2]:
            snp_genes = tr.xpath('td/a/text()').extract()
            snp_id = snp_genes[0]
            gene_id = ';'.join(snp_genes[1:] )
            chrom, pos, strand, allele  = tr.xpath('td/text()').extract()[0:4]
            rec_tmp = '{5}\t{0}\t{1}\t{2}\t{3}\t{4}'.format(chrom, pos, strand, allele, gene_id, snp_id )
            yield {snp_id: rec_tmp}

class GeneSpider(scrapy.Spider):
    name = 'cadgene'
    allowed_domains = 'bioguo.org'
    start_urls = ['http://www.bioguo.org/CADgene/browseAll.php']
    def parse(self, response):
        for tr in response.xpath('//tr')[6:-2]:
            gene_id, symbol, offic_name = tr.xpath('td/a/text()').extract()
            stat_sig, nonsig, trend = tr.xpath('td/font/text()').extract()
            loc, total = tr.xpath('td/text()').extract()[6:]
            loc = loc.strip()
            rec_tmp = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(
            gene_id, symbol, offic_name, loc,
            total, stat_sig, nonsig, trend)
            yield { symbol: rec_tmp }
