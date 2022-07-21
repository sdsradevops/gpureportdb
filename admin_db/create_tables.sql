\connect sbrain_admin_db;
set search_path to sbrain_schema, public;
create extension pgcrypto;

CREATE TABLE IF NOT EXISTS sbrain_schema.environment_sessions
(
    id SERIAL,
    session_id bigint,
    environment_id bigint NOT NULL,
    env_description character varying(2048)  NOT NULL,
    notebook_id bigint NOT NULL,
    session_namespace character varying(256)  NOT NULL,
    session_nodeport_url character varying(256) ,
    session_description character varying(2048)  NOT NULL,
    created_by_user character varying(256)  NOT NULL,
    created_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    captured_timestamp timestamp without time zone default CURRENT_TIMESTAMP,
    status character varying(256)  DEFAULT 'Initializing'::character varying,
    time_begin timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    time_end timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT environment_sessions_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sbrain_schema.terminal_sessions
(   
    id SERIAL,
    session_id bigint NOT NULL,
    terminal_image_id bigint NOT NULL,
    env_description character varying(2048)  NOT NULL,
    terminal_id bigint NOT NULL,
    session_namespace character varying(256)  NOT NULL,
    session_nodeport_url character varying(20480) ,
    session_description character varying(2048)  NOT NULL,
    created_by_user character varying(256)  NOT NULL,
    num_of_terminals integer DEFAULT 0,
    num_of_gpu_per_terminal integer DEFAULT 0,
    num_of_cpu_per_terminal integer DEFAULT 0,
    status character varying(256)  DEFAULT 'INITIATED'::character varying,
    retries integer DEFAULT 0,
    shutdown_requested integer DEFAULT 0,
    auto_clean integer DEFAULT 0,
    message character varying(10000)  DEFAULT ''::character varying,
    created_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    app_ports character varying(256) DEFAULT NULL::character varying,
    time_begin timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    time_end timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT terminal_sessions_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sbrain_schema.namespaces
(
    id SERIAL,
    namespace_name character varying(200) NOT NULL UNIQUE,
    sql_conn_str character varying(1000) NOT NULL,
	schema_name character varying(200) NOT NULL,
    terminal_recoreded_pk bigint DEFAULT 0::INT,
	env_recorded_pk bigint DEFAULT 0::INT,
    CONSTRAINT namspace_pkey PRIMARY KEY (id)
);

INSERT INTO sbrain_schema.namespaces(
	namespace_name, sql_conn_str, schema_name)
	VALUES ('sbrain_db', 'postgresql+psycopg2://postgres:1234@localhost:5434/sbrain_db', 'sbrain_schema');

--INSERT INTO sbrain_schema.namespaces(
--	namespace_name, sql_conn_str, schema_name)
--	VALUES ('sbrain_db1', 'postgresql+psycopg2://postgres:1234@localhost:5434/sbrain_db1', 'sbrain_schema');

CREATE TABLE IF NOT EXISTS sbrain_schema.marker
(
    marker_id SERIAL,
    schema_version character varying(512) COLLATE pg_catalog."default" NOT NULL,
    comment character varying(512) COLLATE pg_catalog."default" NOT NULL,
    created_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT marker_pkey PRIMARY KEY (marker_id),
    CONSTRAINT marker_schema_version_key UNIQUE (schema_version)
);

insert into marker (schema_version, comment) values ('1.0', 'Schema Version 1.0 initialization completed'); 
