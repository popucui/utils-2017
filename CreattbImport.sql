--ALTER TABLE main.browse_dgv RENAME TO old_dgv;
.headers off
DROP TABLE browse_dgv;
CREATE TABLE browse_dgv(
  dgv_id varchar(255),
  chr varchar(25),
  start int,
  stop int,
  varType varchar(255),
  reference text,
  pubmedid int,
  method varchar(255),
  sample int,
  gain int,
  loss int,
  TotalGLInv int,
  Frequency int
);
CREATE INDEX r_dgv on browse_dgv (chr,start,dgv_id);

.mode tabs
.import 'hg19_dgv_2016-05-15_v3.txt' browse_dgv

UPDATE info SET value  = '3.13.0' WHERE key='sqlite-app-version';
UPDATE info SET value='2016-05-15' WHERE key='data-version-dgv';
UPDATE info SET value='2017-01-22' WHERE key='data-version-ucsc';
