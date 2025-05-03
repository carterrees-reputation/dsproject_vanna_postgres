SELECT
  d.datname AS "Database",
  pg_catalog.pg_get_userbyid(d.datdba) AS "Owner",
  pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname)) AS "Size",
  t.spcname AS "Tablespace",
  d.datcollate AS "Collate",
  d.datctype AS "Ctype",
  d.datconnlimit AS "Connection Limit"
FROM
  pg_catalog.pg_database d
JOIN
  pg_catalog.pg_tablespace t ON d.dattablespace = t.oid
ORDER BY
  pg_catalog.pg_database_size(d.datname) DESC;
