#!/usr/bin/env python
#coding=utf-8

import urllib2, json, sys, time
import requests

gene_omim_file = 'genelist_with_omim.xls'
with open(gene_omim_file) as f:
    gene_names = [line.strip().split()[3] for line in f if not line.startswith('chromosome') ]


## do esearch with gene_name
gene_names = set(gene_names)
gene_varid = {}
for gene in gene_names:
    gene_search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={gene}[gene]&retmax=100&retmode=json'.format(**locals() )
    gene_varid[gene] = json.loads(urllib2.urlopen(gene_search_url).read() )
    time.sleep(2)

with open('gene_varid.json','w') as f:
    json.dump(gene_varid, f, indent=2)
## do esummary with varid
with open('gene_varid.json','r') as f:
    gene_varid = json.loads(f.read() )

for gene in gene_varid:
    varid = ','.join(gene_varid[gene]['esearchresult']['idlist'][:20] )

    req = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi', 
    data={'db':'clinvar', 'id':varid, 
    'retmode':'json', 'email':'cuij@newgenegle.com', 
    'tool':'Link2Clinvar'} )
    gene_varid[gene]['esumresult'] = req.json()
    time.sleep(1)

with open('gene_varid_esummary.json', 'w') as f:
    json.dump(gene_varid, f, indent=2)

### add annote info from  gene_varid_esummary.json to genelist_with_omim.xls
with open('gene_varid_esummary.json') as f:
    gene_varid = json.loads(f.read() )

for gene, ssresult in gene_varid.iteritems():
    if ssresult['esearchresult']['count'] == '0': #some gene return none result
        continue
    gene_varid[gene]['trait_names'] = []
    for uid in ssresult['esumresult']['result']['uids']:
        if ssresult['esumresult']['result'][uid].has_key('error'):
        #some varid return error
            continue
        if len(ssresult['esumresult']['result'][uid]['genes'] ) == 1:
            trait_set = ssresult['esumresult']['result'][uid]['trait_set']
            if trait_set:
                gene_varid[gene]['trait_names'].append( trait_set[0]['trait_name'] )
        else:
            pass
    gene_varid[gene]['trait_names'] = [tn for tn in gene_varid[gene]['trait_names'] if tn != 'See cases']
    gene_varid[gene]['trait_names'] = ','.join( list( set(gene_varid[gene]['trait_names']) ) )

result = []
result.append('#OMIM date:2016-01-04\n#ClinVar date:2016-01-06\n')
result.append('chromosome\tregion_start\tregion_end\tgene_name\tlocation\tdisease_omim\tgene_function\tdisease_clinvar\n')
with open(gene_omim_file) as f:
    for line in f:
        if line.startswith('chromosome'):
            continue
        gene_name = line.strip().split()[3]
        if gene_name in gene_varid:
            trait = gene_varid[gene_name]['trait_names'] if gene_varid[gene_name].has_key('trait_names') else ''
            trait_line = '{0}\t{1}\n'.format(
            line.strip('\n'), trait )
        else:
            trait_line = line
        result.append(trait_line)

with open('clinvar_{gene_omim_file}'.format(**locals() ), 'w') as f:
    f.writelines(result)

