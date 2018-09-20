import sys
import urllib2, json, requests
import re

i = 1
clinsig_sgi = {}
egfr_var_id = {}
result = []
with open(sys.argv[1]) as f, open(sys.argv[2]) as clinsig_local, open(sys.argv[3], 'w') as clinvar_db_new:
    for line in f:
        if line.startswith('chrID'):
            result.append(line)
            continue
        chrid, pos, ref, alt, rsid, clin_sig, allelid = line.rstrip().split('\t')
        var_id = allelid.split('/')[-1]
        pos = int(pos)
        if chrid == 'chr7' and ( (55242415 <= pos <= 55242513) or (55248986 <= pos <= 55249171) ):
            egfr_var_id[var_id] = { 'chrid':chrid, 'pos':pos,
                    'ref':ref, 'alt':alt, 'rsid':rsid,
                    'clin_sig': clin_sig, 'allelid':allelid }
        else:
            result.append(line)
    clinvar_db_new.writelines(result)

    for line in clinsig_local:
        if line.startswith('id'):
            continue
        fields = line.rstrip().split('\t')
        clinsig_sgi[i] = '{gene}:{hgvsp}'.format(gene = fields[1], hgvsp = fields[3])
        i += 1
for var_id in egfr_var_id:
    esum_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={id}&retmode=json'.format(id = var_id)
    esum_result = json.loads( requests.get( esum_url ).text )
    title = esum_result['result'][var_id]['title']
    gene_hgvsp_fd = re.findall(r'(?:\()[\w.]+', title)
    gene_hgvsp = [each.lstrip('(') for each in gene_hgvsp_fd]
    gene_hgvsp = ':'.join(gene_hgvsp)

    if gene_hgvsp in clinsig_sgi.values():
        egfr_var_id[var_id]['clin_sig'] = '4-Likely Pathogenic'
        print('change clinical significance for {id}'.format(id = var_id))
    #print(esum_result['result'][var_id]['title'])
    #print(gene_hgvsp)

with open(sys.argv[3], 'a') as f:
    for var_id in egfr_var_id:
        line = '{chrid}\t{pos}\t{ref}\t{alt}\t{rsid}\t{clinsig}\t{allelid}\n'.format(
                chrid = egfr_var_id[var_id]['chrid'], pos = egfr_var_id[var_id]['pos'],
                ref = egfr_var_id[var_id]['ref'], alt = egfr_var_id[var_id]['alt'],
                rsid = egfr_var_id[var_id]['rsid'], allelid = egfr_var_id[var_id]['allelid'],
                clinsig = egfr_var_id[var_id]['clin_sig'],
                )
        f.write(line)
