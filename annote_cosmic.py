import sys
import pymysql

DBCONFIG = {
    'host':'192.168.202.151',
    'user':'annotation',
    'password':'noitatonna',
    'db':'annotation_oncoaim',
    'charset':'utf8mb4',
    'cursorclass':pymysql.cursors.DictCursor,
    }
connection = pymysql.connect(**DBCONFIG)

i = 0
with open(sys.argv[1]) as variant_matrix_fh, open(sys.argv[2], 'w') as variant_matrix_cosmic_fh, connection.cursor() as cursor:
    result = []
    for line in variant_matrix_fh:
        if line.startswith('Locus'):
            # header = line.rstrip() + '\tmutation_id\tmutation_somatic_status\tfathmm_prediction\tfathmm_score\n'
            header = 'cosmic_id\tmutation_somatic_status\tfathmm_prediction\tfathmm_score\t' + line
            result.append(header)
            continue
        fields = line.rstrip().split('\t')
        gene = fields[5]
        hgvsc_abbr = fields[7].split(':')[1]

        sql = "SELECT distinct(mutation_id), mutation_somatic_status, fathmm_prediction, fathmm_score from cosmic_mutantExportCensus_v86 where gene_name=%s AND  mutation_cds=%s"
        cursor.execute(sql, (gene, hgvsc_abbr))
        if i % 20 == 0:
            print('Processing {num} line...'.format(num = i) )
        query_result = cursor.fetchall()
        if cursor.rownumber > 0:

            cosmic_line = '{0}\t{1}\t{2}\t{3}\t'.format(
                query_result[0]['mutation_somatic_status'], query_result[0]['mutation_id'],
                query_result[0]['fathmm_prediction'], query_result[0]['fathmm_score'],
            ) + line
        else:
            cosmic_line = '\t\t\t\t' + line
        result.append(cosmic_line)
        i += 1
    
    variant_matrix_cosmic_fh.writelines(result)




'''
# input tsv line
id	gene_name	accession_number	primary_site	primary_histology	mutation_id	mutation_cds	mutation_aa	mutation_description	grch	mutation_genome_position	mutation_strand	snp	resistance_mutation	fathmm_prediction	fathmm_score	mutation_somatic_status	pubmed_pmid	flag
344367	RET	ENST00000355710	haematopoietic_and_lymphoid_tissue	haematopoietic_neoplasm	COSM3675733	c.200G>A	p.R67H	Substitution - Missense	37	10:43596033-43596033	+	n	-		.50729	Confirmed somatic variant		1
'''
