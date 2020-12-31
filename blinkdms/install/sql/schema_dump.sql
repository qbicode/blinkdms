--
-- PostgreSQL database dump
-- VERSION: 2020-12-22
--

-- Dumped from database version 11.7 (Debian 11.7-0+deb10u1)
-- Dumped by pg_dump version 11.7 (Debian 11.7-0+deb10u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: blinkdms_tab; Type: SCHEMA; Schema: -; Owner: -
--




--
-- Name: sequneces_reset(); Type: FUNCTION; Schema: blinkdms_tab; Owner: -
--

CREATE FUNCTION sequneces_reset() RETURNS integer
    LANGUAGE plpgsql
    AS $$ 
DECLARE
   seq_name text; 
   query text;
   alter_query text;
   rec RECORD;
BEGIN
   query := 'select sequence_name from information_schema.sequences order by sequence_name';
   FOR rec IN EXECUTE query LOOP
      alter_query := 'ALTER SEQUENCE  ' || rec.sequence_name || ' START WITH 1  MINVALUE 1'; 
      RAISE NOTICE '- %', alter_query;
      EXECUTE alter_query;
      
   END LOOP;
   
   RAISE NOTICE 'READY';
   return 1;
END ; 
$$;


SET default_with_oids = false;

--
-- Name: globals; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE globals (
    name character varying(256) NOT NULL,
    value character varying(4000),
    notes character varying(4000)
);

COMMENT ON TABLE globals IS 'globals';
COMMENT ON COLUMN globals.name IS 'key';
COMMENT ON COLUMN globals.value IS 'value of key';
COMMENT ON COLUMN globals.notes IS 'notes';

--
-- Name: globals pk_globals; Type: CONSTRAINT; Schema: blinkdmstab; Owner: -
--

ALTER TABLE ONLY globals
    ADD CONSTRAINT pk_globals PRIMARY KEY (name);



--
-- Name: aud_log; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE aud_log (
    version_id bigint NOT NULL,
    pos bigint NOT NULL,
    db_user_id bigint NOT NULL,
    sign_date timestamp without time zone,
    state_id bigint NOT NULL,
    notes character varying(255)
);


--
-- Name: TABLE aud_log; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE aud_log IS 'audit log';


--
-- Name: COLUMN aud_log.version_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_log.version_id IS 'id of audit log';


--
-- Name: COLUMN aud_log.pos; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_log.pos IS 'pos in log';


--
-- Name: COLUMN aud_log.db_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_log.db_user_id IS 'link to user';


--
-- Name: COLUMN aud_log.sign_date; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_log.sign_date IS 'signature date';


--
-- Name: COLUMN aud_log.state_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_log.state_id IS 'link to state';


--
-- Name: COLUMN aud_log.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_log.notes IS 'comment';


--
-- Name: aud_plan; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE aud_plan (
    doc_id bigint NOT NULL,
    pos bigint NOT NULL,
    db_user_id bigint NOT NULL,
    state_id bigint NOT NULL,
    done bigint,
    parallel bigint,
    last_email_date timestamp without time zone,
    days_warn bigint
);


--
-- Name: TABLE aud_plan; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE aud_plan IS 'audit plan, independent from version';


--
-- Name: COLUMN aud_plan.doc_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_plan.doc_id IS 'id of audit plan';


--
-- Name: COLUMN aud_plan.pos; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_plan.pos IS 'position of user';


--
-- Name: COLUMN aud_plan.db_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_plan.db_user_id IS 'link to user';


--
-- Name: COLUMN aud_plan.state_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_plan.state_id IS 'id of audit status';


--
-- Name: COLUMN aud_plan.done; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_plan.done IS 'done? 0,1';


--
-- Name: COLUMN aud_plan.parallel; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN aud_plan.parallel IS '0 or 1';


--
-- Name: cct_column; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE cct_column (
    table_name character varying(256) NOT NULL,
    column_name character varying(256) NOT NULL,
    app_data_type character varying(256) NOT NULL,
    cct_table_name character varying(256),
    primary_key bigint NOT NULL,
    most_imp_col smallint DEFAULT 0 NOT NULL,
    visible bigint NOT NULL,
    editable smallint DEFAULT 1 NOT NULL,
    pos double precision,
    unique_col smallint DEFAULT 0 NOT NULL,
    not_null smallint DEFAULT 0 NOT NULL,
    nice_name character varying(256),
    id_col bigint,
    flags character varying(256),
    notes text,
    CONSTRAINT ckc_most_imp_col_cct_colu CHECK ((most_imp_col = ANY (ARRAY[0, 1]))),
    CONSTRAINT ckc_not_null_cct_colu CHECK ((not_null = ANY (ARRAY[0, 1]))),
    CONSTRAINT ckc_unique_col_cct_colu CHECK ((unique_col = ANY (ARRAY[0, 1])))
);


--
-- Name: TABLE cct_column; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE cct_column IS 'Describes the columns of the CCT tables. It is to help the applications accessing this database.';


--
-- Name: COLUMN cct_column.table_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.table_name IS 'name of the table';


--
-- Name: COLUMN cct_column.column_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.column_name IS 'name of the column';


--
-- Name: COLUMN cct_column.app_data_type; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.app_data_type IS 'the application data type';


--
-- Name: COLUMN cct_column.cct_table_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.cct_table_name IS 'If the column is a foreign key:table which is referenced by it. Otherwise: NULL*';


--
-- Name: COLUMN cct_column.primary_key; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.primary_key IS 'is this column a primary key (0 = no, 1..n = first..last primary key)';


--
-- Name: COLUMN cct_column.most_imp_col; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.most_imp_col IS 'is this the most important column of its table';


--
-- Name: COLUMN cct_column.visible; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.visible IS 'should this column be visible to the user? (0..unvisible; 1..visible; 2..advanced)';


--
-- Name: COLUMN cct_column.editable; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.editable IS 'is this column editable? (0 = no; 1 = yes)';


--
-- Name: COLUMN cct_column.pos; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.pos IS 'position of this column on the display';


--
-- Name: COLUMN cct_column.unique_col; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.unique_col IS 'is this column a unique index?';


--
-- Name: COLUMN cct_column.not_null; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.not_null IS 'is this column mandatory?';


--
-- Name: COLUMN cct_column.nice_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.nice_name IS 'nice name for the column (especially for foreign keys)';


--
-- Name: COLUMN cct_column.id_col; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.id_col IS 'use this column for comparison of equalness on import (1 = yes)';


--
-- Name: COLUMN cct_column.flags; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_column.flags IS 'container for flags - see internal documentation';


--
-- Name: cct_table; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE cct_table (
    table_name character varying(256) NOT NULL,
    cct_table_name character varying(256),
    nice_name character varying(256) NOT NULL,
    table_type character varying(256),
    internal smallint DEFAULT 0 NOT NULL,
    notes text,
    CONSTRAINT ckc_internal_cct_tabl CHECK ((internal = ANY (ARRAY[0, 1])))
);


--
-- Name: TABLE cct_table; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE cct_table IS 'table of the tables in the cct database.';


--
-- Name: COLUMN cct_table.table_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_table.table_name IS 'name of the table';


--
-- Name: COLUMN cct_table.cct_table_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_table.cct_table_name IS 'name of the parent table*';


--
-- Name: COLUMN cct_table.nice_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_table.nice_name IS 'nice name of the table for display';


--
-- Name: COLUMN cct_table.table_type; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_table.table_type IS 'type of the table (BO, BO_ASSOC, BO_EXT, BO_DYN, SYS, SYS_META)';


--
-- Name: COLUMN cct_table.internal; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN cct_table.internal IS 'should this table be visible to the user or is it internal for partisan?';


--
-- Name: d_link; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE d_link (
    m_doc_id bigint NOT NULL,
    c_doc_id bigint NOT NULL,
    key smallint
);


--
-- Name: TABLE d_link; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE d_link IS 'document has link to other document';


--
-- Name: COLUMN d_link.m_doc_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN d_link.m_doc_id IS 'id of mother doc';


--
-- Name: COLUMN d_link.c_doc_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN d_link.c_doc_id IS 'id of child doc';


--
-- Name: db_user; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE db_user (
    db_user_id integer NOT NULL,
    nick character varying(256) NOT NULL,
    pass_word text NOT NULL,
    email text NOT NULL,
    su smallint DEFAULT 0 NOT NULL,
    login_last timestamp without time zone,
    login_deny smallint DEFAULT 0 NOT NULL,
    logout_last timestamp without time zone,
    notes text,
    full_name character varying(256),
    login_meth character varying(256),
    roles character varying(4000),
    is_active integer DEFAULT 1,
    CONSTRAINT ckc_su_user CHECK ((su = ANY (ARRAY[0, 1])))
);


--
-- Name: TABLE db_user; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE db_user IS 'user of the database';


--
-- Name: COLUMN db_user.db_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.db_user_id IS 'identifier of the user';


--
-- Name: COLUMN db_user.nick; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.nick IS 'nick/login name of the user';


--
-- Name: COLUMN db_user.pass_word; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.pass_word IS 'encrupted password of the user';


--
-- Name: COLUMN db_user.email; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.email IS 'email address of the user (only shown to root)';


--
-- Name: COLUMN db_user.su; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.su IS 'is this user superuser? (1 = yes)';


--
-- Name: COLUMN db_user.login_last; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.login_last IS 'date, when the user logged in for the last time';


--
-- Name: COLUMN db_user.logout_last; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.logout_last IS 'date, when the user logged out for the last time';


--
-- Name: COLUMN db_user.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.notes IS 'annotations to this user';


--
-- Name: COLUMN db_user.full_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN db_user.full_name IS 'full user name';


--
-- Name: db_user_db_user_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE db_user_db_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: db_user_db_user_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE db_user_db_user_id_seq OWNED BY db_user.db_user_id;


--
-- Name: db_user_in_group; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE db_user_in_group (
    user_group_id bigint NOT NULL,
    db_user_id bigint NOT NULL
);


--
-- Name: doc; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE doc (
    doc_id integer NOT NULL,
    c_id character varying(255) NOT NULL,
    doc_type_id bigint NOT NULL,
    notes character varying(4000),
    act_vers_id bigint,
    db_user_id bigint,
    user_group_id bigint,
    wf_plan int,
);


--
-- Name: TABLE doc; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE doc IS 'base document';


--
-- Name: COLUMN doc.doc_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.doc_id IS 'id of document';


--
-- Name: COLUMN doc.c_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.c_id IS 'Customer Doc ID';


--
-- Name: COLUMN doc.doc_type_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.doc_type_id IS 'cocument type';


--
-- Name: COLUMN doc.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.notes IS 'notes';


--
-- Name: COLUMN doc.act_vers_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.act_vers_id IS 'active version ID';


--
-- Name: COLUMN doc.db_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.db_user_id IS 'owner of doc';


--
-- Name: COLUMN doc.user_group_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc.user_group_id IS 'owner group of doc';

COMMENT ON COLUMN doc.wf_plan IS 'workflow plan: 1:RELEASE, 2:WITHDRAW, 3:EDIT';


--
-- Name: doc_doc_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE doc_doc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: doc_doc_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE doc_doc_id_seq OWNED BY doc.doc_id;


--
-- Name: doc_type; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE doc_type (
    doc_type_id integer NOT NULL,
    name character varying(255),
    metadata character varying(4000),
    notes character varying(4000),
    wfl_id bigint
);


--
-- Name: TABLE doc_type; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE doc_type IS 'document type';


--
-- Name: COLUMN doc_type.doc_type_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc_type.doc_type_id IS 'id of document type';


--
-- Name: COLUMN doc_type.name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc_type.name IS 'name of the document type';


--
-- Name: COLUMN doc_type.metadata; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc_type.metadata IS 'JSON structure';


--
-- Name: COLUMN doc_type.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN doc_type.notes IS 'notes';


--
-- Name: doc_type_doc_type_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE doc_type_doc_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: doc_type_doc_type_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE doc_type_doc_type_id_seq OWNED BY doc_type.doc_type_id;


--
-- Name: version; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE version (
    version_id integer NOT NULL,
    name character varying(255),
    doc_id bigint NOT NULL,
    version bigint NOT NULL,
    release_date timestamp without time zone,
    valid_date timestamp without time zone,
    is_active bigint,
    expiry_date timestamp without time zone,
    notes character varying(4000),
    wfl_active integer
);


--
-- Name: TABLE version; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE version IS 'version of document';


--
-- Name: COLUMN version.version_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.version_id IS 'id of document version';


--
-- Name: COLUMN version.name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.name IS 'name of the document version';


--
-- Name: COLUMN version.doc_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.doc_id IS 'link to base document';


--
-- Name: COLUMN version.version; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.version IS 'version number';


--
-- Name: COLUMN version.release_date; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.release_date IS 'release date';


--
-- Name: COLUMN version.valid_date; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.valid_date IS 'date, when doc becomes valid';


--
-- Name: COLUMN version.is_active; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.is_active IS '0 or 1';


--
-- Name: COLUMN version.expiry_date; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.expiry_date IS 'expiry date';


--
-- Name: COLUMN version.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.notes IS 'notes';


--
-- Name: COLUMN version.wfl_active; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN version.wfl_active IS '0 or 1';


--
-- Name: doc_vers_active; Type: VIEW; Schema: blinkdms_tab; Owner: -
--

CREATE VIEW doc_vers_active AS
 SELECT x.version_id,
    x.name,
    x.doc_id,
    x.version,
    x.release_date,
    x.valid_date,
    x.is_active,
    x.expiry_date,
    x.notes,
    x.wfl_active,
    d.c_id,
    d.doc_type_id,
    d.db_user_id,
    d.user_group_id
   FROM (version x
     JOIN doc d ON ((x.doc_id = d.doc_id)))
  WHERE (x.version_id = d.act_vers_id);


--
-- Name: doc_vers_edit; Type: VIEW; Schema: blinkdms_tab; Owner: -
--

CREATE VIEW doc_vers_edit AS
 SELECT x.version_id,
    x.name,
    x.doc_id,
    x.version,
    x.release_date,
    x.valid_date,
    x.is_active,
    x.expiry_date,
    x.notes,
    x.wfl_active,
    d.c_id,
    d.doc_type_id,
    d.db_user_id,
    d.user_group_id
   FROM (version x
     JOIN doc d ON ((x.doc_id = d.doc_id)))
  WHERE (x.version_id IN ( SELECT max(version.version_id) AS max
           FROM version
          GROUP BY version.doc_id));


--
-- Name: proj; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE proj (
    proj_id integer NOT NULL,
    pro_proj_id bigint,
    name character varying(256) NOT NULL,
    notes text,
    typex bigint,
    db_user_id bigint NOT NULL,
    crea_date timestamp without time zone NOT NULL,
    mod_user_id bigint,
    mod_date timestamp without time zone
);


--
-- Name: TABLE proj; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE proj IS 'folder';


--
-- Name: COLUMN proj.proj_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.proj_id IS 'identifier of the project';


--
-- Name: COLUMN proj.pro_proj_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.pro_proj_id IS 'identifier of the parent project*';


--
-- Name: COLUMN proj.name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.name IS 'name of the project';


--
-- Name: COLUMN proj.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.notes IS 'annotations to this project';


--
-- Name: COLUMN proj.typex; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.typex IS 'special type of project';


--
-- Name: COLUMN proj.db_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.db_user_id IS 'creator of folder';


--
-- Name: COLUMN proj.crea_date; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.crea_date IS 'creation date';


--
-- Name: COLUMN proj.mod_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.mod_user_id IS 'modifier of folder';


--
-- Name: COLUMN proj.mod_date; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj.mod_date IS 'mod date';


--
-- Name: proj_has_elem; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE proj_has_elem (
    proj_id bigint NOT NULL,
    doc_id bigint NOT NULL,
    is_link smallint
);


--
-- Name: TABLE proj_has_elem; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE proj_has_elem IS 'project has business obeject elements';


--
-- Name: COLUMN proj_has_elem.doc_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN proj_has_elem.doc_id IS 'link to document in project';


--
-- Name: proj_proj_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE proj_proj_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: proj_proj_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE proj_proj_id_seq OWNED BY proj.proj_id;


--
-- Name: state; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE state (
    state_id integer NOT NULL,
    name character varying(255),
    nice character varying(255),
    action_str character varying(255) NOT NULL
);


--
-- Name: TABLE state; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE state IS 'audit status definitions';


--
-- Name: COLUMN state.state_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN state.state_id IS 'id of audit status definitions';


--
-- Name: COLUMN state.name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN state.name IS 'name of the audit status definitions';


--
-- Name: COLUMN state.nice; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN state.nice IS 'nice name';


--
-- Name: COLUMN state.action_str; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN state.action_str IS 'activity: e.g. review';


--
-- Name: state_state_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE state_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: state_state_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE state_state_id_seq OWNED BY state.state_id;


--
-- Name: sys_a_log; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE sys_a_log (
    datex timestamp without time zone NOT NULL,
    ipaddr character varying(256) NOT NULL,
    user_nick character varying(256),
    keyx character varying(256),
    message character varying(4000) NOT NULL
);


--
-- Name: TABLE sys_a_log; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE sys_a_log IS 'system alarm log';


--
-- Name: COLUMN sys_a_log.datex; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN sys_a_log.datex IS 'date of event';


--
-- Name: COLUMN sys_a_log.ipaddr; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN sys_a_log.ipaddr IS 'IP address of remote computer';


--
-- Name: COLUMN sys_a_log.user_nick; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN sys_a_log.user_nick IS 'nickname of tried login, can be empty';


--
-- Name: COLUMN sys_a_log.keyx; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN sys_a_log.keyx IS 'key of event; e.g. "LOGIN"';


--
-- Name: COLUMN sys_a_log.message; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN sys_a_log.message IS 'detailed message';


--
-- Name: uploads; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE uploads (
    version_id bigint NOT NULL,
    pos bigint NOT NULL,
    name character varying(255) NOT NULL,
    xtype character varying(255),
    has_pdf smallint
);


--
-- Name: TABLE uploads; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE uploads IS 'uploads';


--
-- Name: COLUMN uploads.version_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN uploads.version_id IS 'id of uploads';


--
-- Name: COLUMN uploads.pos; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN uploads.pos IS 'pos';


--
-- Name: COLUMN uploads.name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN uploads.name IS 'upload name';


--
-- Name: COLUMN uploads.xtype; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN uploads.xtype IS 'e.g. S_DOC';


--
-- Name: COLUMN uploads.has_pdf; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN uploads.has_pdf IS '0 or 1 : upload has a PDF document?';


--
-- Name: user_group; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE user_group (
    user_group_id integer NOT NULL,
    db_user_id bigint NOT NULL,
    name character varying(256) NOT NULL,
    notes character varying(4000),
    single_user bigint,
    master_group_id bigint,
    inactive bigint,
    typex integer
);


--
-- Name: user_group_user_group_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE user_group_user_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_group_user_group_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE user_group_user_group_id_seq OWNED BY user_group.user_group_id;


--
-- Name: user_pref; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE user_pref (
    db_user_id bigint NOT NULL,
    var_name character varying(256) NOT NULL,
    value text,
    no_cache bigint,
    upflag integer
);


--
-- Name: TABLE user_pref; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE user_pref IS 'personal preferences of the users';


--
-- Name: COLUMN user_pref.db_user_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN user_pref.db_user_id IS 'identifier of the user';


--
-- Name: COLUMN user_pref.var_name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN user_pref.var_name IS 'name of the variable';


--
-- Name: COLUMN user_pref.value; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN user_pref.value IS 'value of the variable';


--
-- Name: COLUMN user_pref.no_cache; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN user_pref.no_cache IS '[0],1 no caching?';


--
-- Name: COLUMN user_pref.upflag; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN user_pref.upflag IS 'flag, if variable is used; 0:not used, 1:used';


--
-- Name: version_version_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE version_version_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: version_version_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE version_version_id_seq OWNED BY version.version_id;


--
-- Name: wfl; Type: TABLE; Schema: blinkdms_tab; Owner: -
--

CREATE TABLE wfl (
    wfl_id integer NOT NULL,
    name character varying(255),
    keyx character varying(255),
    metadata character varying(4000),
    notes character varying(4000)
);


--
-- Name: TABLE wfl; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON TABLE wfl IS 'document workflow';


--
-- Name: COLUMN wfl.wfl_id; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN wfl.wfl_id IS 'id of workflow';


--
-- Name: COLUMN wfl.name; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN wfl.name IS 'name of workflow';


--
-- Name: COLUMN wfl.keyx; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN wfl.keyx IS 'Key of workflow';


--
-- Name: COLUMN wfl.metadata; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN wfl.metadata IS 'JSON data of workflow';


--
-- Name: COLUMN wfl.notes; Type: COMMENT; Schema: blinkdms_tab; Owner: -
--

COMMENT ON COLUMN wfl.notes IS 'notes';


--
-- Name: wfl_wfl_id_seq; Type: SEQUENCE; Schema: blinkdms_tab; Owner: -
--

CREATE SEQUENCE wfl_wfl_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wfl_wfl_id_seq; Type: SEQUENCE OWNED BY; Schema: blinkdms_tab; Owner: -
--

ALTER SEQUENCE wfl_wfl_id_seq OWNED BY wfl.wfl_id;

--- s_vario

CREATE TABLE s_vario (
	table_name varchar(255) NOT NULL,
	obj_id bigint NOT NULL,
	key varchar(255) NOT NULL,
	value text,
	CONSTRAINT pk_s_vario PRIMARY KEY (table_name,obj_id,key)
) ;
COMMENT ON TABLE s_vario IS E'variable key value pairs for objects';
COMMENT ON COLUMN s_vario.value IS E'value';
COMMENT ON COLUMN s_vario.key IS E'key';
COMMENT ON COLUMN s_vario.obj_id IS E'ID of object';
COMMENT ON COLUMN s_vario.table_name IS E'id of table';
CREATE INDEX s_vario_ak2 ON s_vario (obj_id);

CREATE TABLE s_vario_desc (
	table_name varchar(255) NOT NULL,
	key varchar(255) NOT NULL,
	nice varchar(255),
	exim bigint,
	editable bigint,
	notes text,
	CONSTRAINT pk_s_vario_desc PRIMARY KEY (table_name,key)
) ;
COMMENT ON TABLE s_vario_desc IS E'definition of S_VARIO keys';
COMMENT ON COLUMN s_vario_desc.table_name IS E'id of table';
COMMENT ON COLUMN s_vario_desc.notes IS E'notes';
COMMENT ON COLUMN s_vario_desc.nice IS E'nice name of key';
COMMENT ON COLUMN s_vario_desc.editable IS E'is this column editable? ';
COMMENT ON COLUMN s_vario_desc.exim IS E'deny export flag';
COMMENT ON COLUMN s_vario_desc.key IS E'key';


ALTER TABLE s_vario_desc ADD CONSTRAINT fk_cct_table2s_vario_desc FOREIGN KEY (table_name) REFERENCES cct_table(table_name) ON DELETE NO ACTION NOT DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE s_vario ADD CONSTRAINT fk_cct_table2s_vario FOREIGN KEY (table_name) REFERENCES cct_table(table_name) ON DELETE NO ACTION NOT DEFERRABLE INITIALLY IMMEDIATE;


--
-- Name: db_user db_user_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY db_user ALTER COLUMN db_user_id SET DEFAULT nextval('db_user_db_user_id_seq'::regclass);


--
-- Name: doc doc_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc ALTER COLUMN doc_id SET DEFAULT nextval('doc_doc_id_seq'::regclass);


--
-- Name: doc_type doc_type_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc_type ALTER COLUMN doc_type_id SET DEFAULT nextval('doc_type_doc_type_id_seq'::regclass);


--
-- Name: proj proj_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY proj ALTER COLUMN proj_id SET DEFAULT nextval('proj_proj_id_seq'::regclass);


--
-- Name: state state_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY state ALTER COLUMN state_id SET DEFAULT nextval('state_state_id_seq'::regclass);


--
-- Name: user_group user_group_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY user_group ALTER COLUMN user_group_id SET DEFAULT nextval('user_group_user_group_id_seq'::regclass);


--
-- Name: version version_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY version ALTER COLUMN version_id SET DEFAULT nextval('version_version_id_seq'::regclass);


--
-- Name: wfl wfl_id; Type: DEFAULT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY wfl ALTER COLUMN wfl_id SET DEFAULT nextval('wfl_wfl_id_seq'::regclass);


--
-- Data for Name: aud_log; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY aud_log (version_id, pos, db_user_id, sign_date, state_id, notes) FROM stdin;
\.


--
-- Data for Name: aud_plan; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY aud_plan (doc_id, pos, db_user_id, state_id, done, parallel, last_email_date, days_warn) FROM stdin;
\.


COPY globals (name, value, notes) FROM stdin;
db.version	1.0 2020-12-22	Version of DB
\.

--
-- Data for Name: cct_column; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY cct_column (table_name, column_name, app_data_type, cct_table_name, primary_key, most_imp_col, visible, editable, pos, unique_col, not_null, nice_name, id_col, flags, notes) FROM stdin;
AUD_PLAN	DOC_ID	ID	\N	1	0	1	1	1	0	1	doc_id	\N	\N	\N
AUD_PLAN	POS	ID	\N	2	0	1	1	2	0	1	pos	\N	\N	\N
DOC	DOC_ID	ID	\N	1	0	1	1	1	0	1	doc_id	\N	\N	\N
PROJ	PROJ_ID	ID	\N	1	0	1	1	1	0	1	proj_id	\N	\N	\N
PROJ_HAS_ELEM	PROJ_ID	ID	\N	1	0	1	1	1	0	1	proj_id	\N	\N	\N
PROJ_HAS_ELEM	DOC_ID	ID	\N	2	0	1	1	2	0	1	doc_id	\N	\N	\N
STATE	STATE_ID	ID	\N	1	0	1	1	1	0	1	state_id	\N	\N	\N
UPLOADS	VERSION_ID	ID	\N	1	0	1	1	1	0	1	version_id	\N	\N	\N
UPLOADS	POS	ID	\N	2	0	1	1	2	0	1	pos	\N	\N	\N
VERSION	VERSION_ID	ID	\N	1	0	1	1	1	0	1	version_id	\N	\N	\N
AUD_LOG	VERSION_ID	ID	\N	1	0	1	1	1	0	1	version_id	\N	\N	\N
AUD_LOG	POS	ID	\N	2	0	1	1	2	0	1	pos	\N	\N	\N
DOC_VERS_EDIT	VERSION_ID	ID	\N	1	0	1	1	1	0	1	version_id	\N	\N	\N
DOC_VERS_ACTIVE	VERSION_ID	ID	\N	1	0	1	1	1	0	1	version_id	\N	\N	\N
DB_USER	DB_USER_ID	ID	\N	1	0	1	0	1	0	1	\N	\N	\N	\N
DB_USER	EMAIL	EMAIL	\N	0	0	1	1	5	0	1	email	\N	\N	\N
DB_USER	FULL_NAME	STRING	\N	0	0	1	1	6	0	0	full name	\N	\N	\N
DB_USER	LOGIN_LAST	DATE	\N	0	0	1	0	8	0	0	\N	\N	\N	\N
DB_USER	LOGIN_DENY	BOOLEAN	\N	0	0	1	1	9	0	0	\N	\N	\N	\N
DB_USER	LOGOUT_LAST	DATE	\N	0	0	1	0	10	0	0	\N	\N	\N	\N
DB_USER	SU	BOOLEAN	\N	0	0	1	2	12	0	0	\N	\N	\N	\N
DB_USER	NOTES	NOTES	\N	0	0	1	1	18	0	0	\N	\N	\N	\N
DB_USER	PASS_WORD	PASSWORD	\N	0	0	0	0	15	0	1	\N	\N	\N	\N
DB_USER	NICK	NAME	\N	0	1	1	1	2	1	1	\N	\N	\N	\N
DOC	C_ID	NAME	\N	0	1	1	1	2	1	1	Doc ID	\N	\N	\N
DOC	DOC_TYPE_ID	ID	DOC_TYPE	0	0	1	1	3	0	1	Doc type	\N	\N	\N
DOC	ACT_VERS_ID	ID	VERSION	0	0	1	1	4	0	0	Active Version	\N	\N	\N
DOC	NOTES	NOTES	\N	0	0	1	1	5	0	0	Notes	\N	\N	\N
PROJ	NAME	NAME	\N	0	1	1	1	2	0	1	name	\N	\N	\N
USER_GROUP	USER_GROUP_ID	ID	\N	1	0	1	0	1	0	1	group ID	\N	\N	\N
USER_GROUP	DB_USER_ID	ID	DB_USER	0	0	1	1	2	0	0	owner id	\N	\N	\N
USER_GROUP	NAME	NAME	\N	0	1	1	1	3	1	1	NAME	\N	\N	\N
USER_GROUP	NOTES	NOTES	\N	0	0	1	1	4	0	0	NOTES	\N	\N	\N
USER_GROUP	SINGLE_USER	INT	\N	0	0	1	1	5	0	0	SINGLE_USER	\N	\N	\N
USER_GROUP	MASTER_GROUP_ID	ID	USER_GROUP	0	0	1	1	6	0	0	MASTER_GROUP ID	\N	\N	\N
USER_GROUP	INACTIVE	INT	\N	0	0	1	1	7	0	0	INACTIVE	\N	\N	\N
USER_GROUP	TYPEX	INT	\N	0	0	1	1	8	0	0	TYPEX	\N	\N	\N
DB_USER_IN_GROUP	USER_GROUP_ID	ID	USER_GROUP	1	1	1	1	1	0	1	group ID	\N	\N	\N
DB_USER_IN_GROUP	DB_USER_ID	ID	DB_USER	2	0	1	1	2	0	1	user id	\N	\N	\N
STATE	NAME	NAME	\N	0	1	1	1	2	1	1	Key	\N	\N	\N
STATE	NICE	NAME	\N	0	0	1	1	3	0	1	nice name	\N	\N	\N
STATE	ACTION_STR	NAME	\N	0	0	1	1	4	0	0	action string	\N	\N	\N
D_LINK	C_DOC_ID	ID	DOC	2	0	1	1	2	0	1	child doc_id	\N	\N	\N
D_LINK	M_DOC_ID	ID	DOC	1	0	1	1	1	0	1	mother doc_id	\N	\N	\N
DOC	DB_USER_ID	ID	DB_USER	0	0	1	1	4.5	0	0	owner	\N	\N	\N
DOC	USER_GROUP_ID	ID	USER_GROUP	0	0	1	1	4.59999999999999964	0	0	owner group	\N	\N	\N
CCT_TABLE	NOTES	NOTES	\N	0	0	1	1	15	0	0	notes	\N	\N	\N
DOC_TYPE	DOC_TYPE_ID	ID	\N	1	0	1	1	1	0	1	doc_type_id	\N	\N	\N
DOC_TYPE	METADATA	STRING	\N	0	0	1	3	3	0	0	meta data	\N	\N	JSON data
DOC_TYPE	NAME	NAME	\N	0	1	1	1	2	1	1	name	\N	\N	name of type
DOC_TYPE	NOTES	NOTES	\N	0	0	0	1	4	0	1	notes	\N	\N	\N
CCT_TABLE	TABLE_NAME	NAME	\N	1	1	1	1	1	1	1	\N	\N	\N	\N
CCT_TABLE	NICE_NAME	NAME	\N	0	0	1	1	2	1	1	\N	\N	\N	\N
CCT_TABLE	CCT_TABLE_NAME	NAME	CCT_TABLE	0	0	1	1	3	0	0	mother table	\N	\N	\N
CCT_TABLE	TABLE_TYPE	NAME	\N	0	0	1	1	4	0	0	\N	\N	\N	\N
CCT_TABLE	INTERNAL	BOOLEAN	\N	0	0	1	1	6	0	0	intern	\N	\N	\N
DB_USER	LOGIN_METH	NAME	\N	0	0	1	1	7	0	0	login method	\N	\N	\N
SYS_A_LOG	DATEX	DATE	\N	1	0	1	1	1	0	1	entry date	\N	\N	\N
SYS_A_LOG	IPADDR	NAME	\N	2	0	1	1	2	0	1	IP address	\N	\N	\N
SYS_A_LOG	USER_NICK	NAME	\N	0	0	1	1	1	0	1	user nick	\N	\N	\N
SYS_A_LOG	KEYX	NAME	\N	2	0	1	1	2	0	1	key	\N	\N	\N
SYS_A_LOG	MESSAGE	NOTES	\N	2	0	1	1	2	0	1	notes	\N	\N	\N
DB_USER	ROLES	NAME	\N	0	0	1	0	11	0	0	roles	\N	\N	\N
CCT_COLUMN	NOT_NULL	BOOLEAN	\N	0	0	1	1	10	0	0	\N	\N	\N	\N
CCT_COLUMN	NICE_NAME	NAME	\N	0	0	1	1	11	0	0	\N	\N	\N	\N
CCT_COLUMN	POS	FLOAT	\N	0	0	1	1	12	0	0	\N	\N	\N	\N
AUD_PLAN	DB_USER_ID	ID	DB_USER	0	0	1	1	3	0	1	DB_USER_ID	\N	\N	\N
AUD_PLAN	STATE_ID	ID	STATE	0	0	1	1	4	0	0	STATE_ID	\N	\N	\N
AUD_PLAN	DONE	INT	\N	0	0	1	1	5	0	0	DONE	\N	\N	\N
AUD_PLAN	PARALLEL	INT	\N	0	0	1	1	6	0	0	PARALLEL	\N	\N	\N
AUD_PLAN	LAST_EMAIL_DATE	DATE	\N	0	0	1	1	7	0	0	LAST_EMAIL_DATE	\N	\N	\N
AUD_PLAN	DAYS_WARN	INT	\N	0	0	1	1	8	0	0	DAYS_WARN	\N	\N	\N
CCT_COLUMN	ID_COL	NAME	\N	0	0	1	1	15	0	1	ID col	\N	\N	\N
CCT_COLUMN	TABLE_NAME	NAME	\N	1	0	1	1	1	0	1	table name	\N	\N	\N
CCT_COLUMN	FLAGS	NAME	\N	0	0	1	1	17	0	1	flags	\N	\N	\N
CCT_COLUMN	COLUMN_NAME	NAME	\N	2	1	1	1	2	0	1	column name	\N	\N	\N
CCT_COLUMN	CCT_TABLE_NAME	NAME	CCT_TABLE	0	0	1	1	3	0	0	mother table	\N	\N	\N
CCT_COLUMN	APP_DATA_TYPE	ID	\N	0	0	1	1	4	0	1	\N	\N	\N	\N
CCT_COLUMN	PRIMARY_KEY	NATURAL NUMBER	\N	0	0	1	1	5	0	1	\N	\N	\N	\N
CCT_COLUMN	MOST_IMP_COL	BOOLEAN	\N	0	0	1	1	6	0	1	\N	\N	\N	\N
CCT_COLUMN	VISIBLE	NATURAL NUMBER	\N	0	0	1	1	7	0	1	\N	\N	\N	\N
CCT_COLUMN	EDITABLE	INTEGER	\N	0	0	1	1	8	0	0	\N	\N	\N	\N
CCT_COLUMN	UNIQUE_COL	BOOLEAN	\N	0	0	1	1	9	0	0	\N	\N	\N	\N
CCT_COLUMN	NOTES	NOTES	\N	0	0	1	1	16	0	0	notes	\N	\N	\N
WFL	WFL_ID	ID	\N	1	0	1	1	1	0	1	WFL_ID	\N	\N	\N
WFL	NAME	NAME	\N	0	1	1	1	2	0	1	name	\N	\N	\N
WFL	KEYX	NAME	\N	0	0	1	1	3	0	0	KEYX	\N	\N	\N
WFL	METADATA	NOTES	\N	0	0	1	0	4	0	0	METADATA	\N	\N	\N
WFL	NOTES	NOTES	\N	0	0	1	1	5	0	0	NOTES	\N	\N	\N
DOC_TYPE	WFL_ID	ID	WFL	0	0	1	1	3	0	1	\N	\N	\N	\N
DB_USER	IS_ACTIVE	BOOLEAN	\N	0	0	1	1	16	0	0	user is active	\N	\N	user is active?
\.


--
-- Data for Name: cct_table; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY cct_table (table_name, cct_table_name, nice_name, table_type, internal, notes) FROM stdin;
CCT_TABLE	\N	CCT_TABLE	SYS	0	\N
PROJ	\N	PROJ	SYS	0	\N
PROJ_HAS_ELEM	\N	PROJ_HAS_ELEM	SYS	0	\N
STATE	\N	STATE	SYS	0	\N
VERSION	\N	VERSION	SYS	0	\N
DOC_VERS_EDIT	\N	DOC_VERS_EDIT	SYS	0	\N
DOC_VERS_ACTIVE	\N	DOC_VERS_ACTIVE	SYS	0	\N
AUD_LOG	VERSION	audit log	SYS	0	\N
AUD_PLAN	DOC	AUD_PLAN	SYS	0	\N
DOC	\N	DOC	BO	0	\N
UPLOADS	VERSION	UPLOADS	SYS	0	\N
USER_GROUP	\N	user group	SYS	0	user group
DB_USER_IN_GROUP	USER_GROUP	user in group	SYS_ASSOC	0	user in group
D_LINK	DOC	document link	SYS	0	\N
DB_USER	\N	user	SYS	0	\N
DOC_TYPE	\N	document type	SYS	0	\N
SYS_A_LOG	\N	system alert log	SYS	0	\N
CCT_COLUMN	CCT_TABLE	CCT_COLUMN	SYS	0	\N
WFL	\N	workflow type	SYS	1	workflow type
\.




COPY wfl (wfl_id, name, keyx, metadata, notes) FROM stdin;
1	Normal - only RELEASER	REL_ONLY	\N	\N
2	Advanced - also review	REV_REL	\N	REVIEW + RELEASE
\.


--
-- Data for Name: d_link; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY d_link (m_doc_id, c_doc_id, key) FROM stdin;
\.


--
-- Data for Name: db_user; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY db_user (db_user_id, nick, pass_word, email, su, login_last, login_deny, logout_last, notes, full_name, login_meth, roles) FROM stdin;
1	root	nopasswd	noemail@blink-dx.com	0	2020-12-17 16:52:33	0	\N	\N	Root account	\N	\N
\.





--
-- Data for Name: doc_type; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY doc_type (doc_type_id, name, metadata, notes, wfl_id) FROM stdin;
1	Formular	{"DOC_CODE": "FO", "NUM_DIGITS": "4", "WORD_CONVERT": 0}	\N	1
\.






--
-- Data for Name: state; Type: TABLE DATA; Schema: blinkdms_tab; Owner: -
--

COPY state (state_id, name, nice, action_str) FROM stdin;
1	REL_START	Release Workflow Started	Start Release Workflow
2	REL_END	Released	Release
3	REJECT	Rejected	Reject
4	CREATED	Created	Create
5	REVIEW	Reviewed	Review
6	REVIEW_REL	Reviewed for release	Review for release
\.






--
-- Name: db_user_db_user_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('db_user_db_user_id_seq', 1, true);


--
-- Name: doc_doc_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('doc_doc_id_seq', 1, false);


--
-- Name: doc_type_doc_type_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('doc_type_doc_type_id_seq', 1, true);


--
-- Name: proj_proj_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('proj_proj_id_seq', 1, true);


--
-- Name: state_state_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('state_state_id_seq', 6, true);


--
-- Name: user_group_user_group_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('user_group_user_group_id_seq', 1, false);


--
-- Name: version_version_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('version_version_id_seq', 1, false);


--
-- Name: wfl_wfl_id_seq; Type: SEQUENCE SET; Schema: blinkdms_tab; Owner: -
--

SELECT pg_catalog.setval('wfl_wfl_id_seq', 1, false);


--
-- Name: doc ak_doc_c_id; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc
    ADD CONSTRAINT ak_doc_c_id UNIQUE (c_id);


--
-- Name: user_group ak_name; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY user_group
    ADD CONSTRAINT ak_name UNIQUE (name);


--
-- Name: db_user ak_user; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY db_user
    ADD CONSTRAINT ak_user UNIQUE (nick);


--
-- Name: aud_log pk_aud_log; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_log
    ADD CONSTRAINT pk_aud_log PRIMARY KEY (version_id, pos);


--
-- Name: aud_plan pk_aud_plan; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_plan
    ADD CONSTRAINT pk_aud_plan PRIMARY KEY (doc_id, pos);


--
-- Name: cct_column pk_cct_column; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY cct_column
    ADD CONSTRAINT pk_cct_column PRIMARY KEY (table_name, column_name);


--
-- Name: cct_table pk_cct_table; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY cct_table
    ADD CONSTRAINT pk_cct_table PRIMARY KEY (table_name);


--
-- Name: db_user pk_db_user; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY db_user
    ADD CONSTRAINT pk_db_user PRIMARY KEY (db_user_id);


--
-- Name: db_user_in_group pk_db_user_in_group; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY db_user_in_group
    ADD CONSTRAINT pk_db_user_in_group PRIMARY KEY (user_group_id, db_user_id);


--
-- Name: doc pk_doc; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc
    ADD CONSTRAINT pk_doc PRIMARY KEY (doc_id);


--
-- Name: doc_type pk_doc_type; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc_type
    ADD CONSTRAINT pk_doc_type PRIMARY KEY (doc_type_id);


--
-- Name: d_link pk_f_link; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY d_link
    ADD CONSTRAINT pk_f_link PRIMARY KEY (m_doc_id, c_doc_id);


--
-- Name: proj pk_proj; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY proj
    ADD CONSTRAINT pk_proj PRIMARY KEY (proj_id);


--
-- Name: proj_has_elem pk_proj_has_elem; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY proj_has_elem
    ADD CONSTRAINT pk_proj_has_elem PRIMARY KEY (proj_id, doc_id);


--
-- Name: state pk_state; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY state
    ADD CONSTRAINT pk_state PRIMARY KEY (state_id);


--
-- Name: sys_a_log pk_sys_a_log; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY sys_a_log
    ADD CONSTRAINT pk_sys_a_log PRIMARY KEY (datex, ipaddr);


--
-- Name: uploads pk_uploads; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY uploads
    ADD CONSTRAINT pk_uploads PRIMARY KEY (version_id, pos);


--
-- Name: user_group pk_user_group; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY user_group
    ADD CONSTRAINT pk_user_group PRIMARY KEY (user_group_id);


--
-- Name: user_pref pk_user_pref; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY user_pref
    ADD CONSTRAINT pk_user_pref PRIMARY KEY (db_user_id, var_name);


--
-- Name: version pk_version; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY version
    ADD CONSTRAINT pk_version PRIMARY KEY (version_id);


--
-- Name: wfl pk_wfl_id; Type: CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY wfl
    ADD CONSTRAINT pk_wfl_id PRIMARY KEY (wfl_id);


--
-- Name: cct_column_fk2; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX cct_column_fk2 ON cct_column USING btree (table_name);


--
-- Name: cct_column_fk3; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX cct_column_fk3 ON cct_column USING btree (cct_table_name);


--
-- Name: cct_table_fk; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX cct_table_fk ON cct_table USING btree (cct_table_name);


--
-- Name: d_link_fk1; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX d_link_fk1 ON d_link USING btree (m_doc_id);


--
-- Name: d_link_fk2; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX d_link_fk2 ON d_link USING btree (c_doc_id);


--
-- Name: doc_type_ak2; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX doc_type_ak2 ON doc_type USING btree (name);


--
-- Name: proj_ak2; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX proj_ak2 ON proj USING btree (name);


--
-- Name: proj_fk; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX proj_fk ON proj USING btree (pro_proj_id);


--
-- Name: proj_has_elem_fk; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX proj_has_elem_fk ON proj_has_elem USING btree (proj_id);


--
-- Name: state_ak2; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX state_ak2 ON state USING btree (name);


--
-- Name: sys_a_log_ind; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX sys_a_log_ind ON sys_a_log USING btree (datex);


--
-- Name: user_pref_fk; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX user_pref_fk ON user_pref USING btree (db_user_id);


--
-- Name: version_ak2; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX version_ak2 ON version USING btree (name);


--
-- Name: wfl_ind1; Type: INDEX; Schema: blinkdms_tab; Owner: -
--

CREATE INDEX wfl_ind1 ON wfl USING btree (name);


--
-- Name: aud_log fk_db_user2aud_log; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_log
    ADD CONSTRAINT fk_db_user2aud_log FOREIGN KEY (db_user_id) REFERENCES db_user(db_user_id);


--
-- Name: aud_plan fk_db_user2aud_plan; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_plan
    ADD CONSTRAINT fk_db_user2aud_plan FOREIGN KEY (db_user_id) REFERENCES db_user(db_user_id);


--
-- Name: db_user_in_group fk_db_user2db_user_in_group; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY db_user_in_group
    ADD CONSTRAINT fk_db_user2db_user_in_group FOREIGN KEY (db_user_id) REFERENCES db_user(db_user_id) ON DELETE CASCADE;


--
-- Name: doc fk_db_user2doc; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc
    ADD CONSTRAINT fk_db_user2doc FOREIGN KEY (db_user_id) REFERENCES db_user(db_user_id);


--
-- Name: proj fk_db_user2proj; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY proj
    ADD CONSTRAINT fk_db_user2proj FOREIGN KEY (db_user_id) REFERENCES db_user(db_user_id);


--
-- Name: proj fk_db_user2proj2; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY proj
    ADD CONSTRAINT fk_db_user2proj2 FOREIGN KEY (mod_user_id) REFERENCES db_user(db_user_id);


--
-- Name: user_pref fk_db_user2user_pref; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY user_pref
    ADD CONSTRAINT fk_db_user2user_pref FOREIGN KEY (db_user_id) REFERENCES db_user(db_user_id) ON DELETE CASCADE;


--
-- Name: aud_plan fk_doc2aud_plan; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_plan
    ADD CONSTRAINT fk_doc2aud_plan FOREIGN KEY (doc_id) REFERENCES doc(doc_id) ON DELETE CASCADE;


--
-- Name: d_link fk_doc2d_link1; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY d_link
    ADD CONSTRAINT fk_doc2d_link1 FOREIGN KEY (m_doc_id) REFERENCES doc(doc_id);


--
-- Name: d_link fk_doc2d_link2; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY d_link
    ADD CONSTRAINT fk_doc2d_link2 FOREIGN KEY (c_doc_id) REFERENCES doc(doc_id);


--
-- Name: proj_has_elem fk_doc2proj_has_elem; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY proj_has_elem
    ADD CONSTRAINT fk_doc2proj_has_elem FOREIGN KEY (doc_id) REFERENCES doc(doc_id);


--
-- Name: version fk_doc2version; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY version
    ADD CONSTRAINT fk_doc2version FOREIGN KEY (doc_id) REFERENCES doc(doc_id);


--
-- Name: doc fk_doc_type2doc; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc
    ADD CONSTRAINT fk_doc_type2doc FOREIGN KEY (doc_type_id) REFERENCES doc_type(doc_type_id);


--
-- Name: doc fk_doc_type2version; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc
    ADD CONSTRAINT fk_doc_type2version FOREIGN KEY (act_vers_id) REFERENCES version(version_id);


--
-- Name: aud_log fk_state2aud_log; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_log
    ADD CONSTRAINT fk_state2aud_log FOREIGN KEY (state_id) REFERENCES state(state_id);


--
-- Name: aud_plan fk_state2aud_plan; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_plan
    ADD CONSTRAINT fk_state2aud_plan FOREIGN KEY (state_id) REFERENCES state(state_id);


--
-- Name: db_user_in_group fk_user_group2db_user_in_group; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY db_user_in_group
    ADD CONSTRAINT fk_user_group2db_user_in_group FOREIGN KEY (user_group_id) REFERENCES user_group(user_group_id) ON DELETE CASCADE;


--
-- Name: doc fk_user_group2doc; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc
    ADD CONSTRAINT fk_user_group2doc FOREIGN KEY (user_group_id) REFERENCES user_group(user_group_id);


--
-- Name: aud_log fk_version2aud_log; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY aud_log
    ADD CONSTRAINT fk_version2aud_log FOREIGN KEY (version_id) REFERENCES version(version_id) ON DELETE CASCADE;


--
-- Name: uploads fk_version2uploads; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY uploads
    ADD CONSTRAINT fk_version2uploads FOREIGN KEY (version_id) REFERENCES version(version_id) ON DELETE CASCADE;


--
-- Name: doc_type fk_wfl2doc_type; Type: FK CONSTRAINT; Schema: blinkdms_tab; Owner: -
--

ALTER TABLE ONLY doc_type
    ADD CONSTRAINT fk_wfl2doc_type FOREIGN KEY (wfl_id) REFERENCES wfl(wfl_id);


--
-- PostgreSQL database dump complete
--

