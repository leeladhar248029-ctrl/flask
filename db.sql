-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.users (
  id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  name character varying NOT NULL,
  username character varying UNIQUE,
  bio character varying,
  email character varying UNIQUE,
  password character varying,
  CONSTRAINT users_pkey PRIMARY KEY (id)
);