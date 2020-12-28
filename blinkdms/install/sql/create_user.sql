CREATE ROLE blinkdms_user;
create user blinkdms with password 'XXX';
grant all privileges on database dmsdb to blinkdms;
CREATE SCHEMA blinkdms_tab AUTHORIZATION blinkdms;
ALTER SCHEMA blinkdms_tab OWNER TO blinkdms;
/* change search_path for user */
alter role blinkdms set search_path = blinkdms_tab, pg_catalog;