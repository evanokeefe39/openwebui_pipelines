-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your documents
create table n8n_rag_1_docs_users (
  id bigserial primary key,
  content text, -- corresponds to Document.pageContent
  metadata jsonb, -- corresponds to Document.metadata
  embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
);

-- Create a function to search for documents
create or replace function match_docs_n8n_rag_1_docs_users (
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{}'
) returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (n8n_rag_1_docs_users.embedding <=> query_embedding) as similarity
  from n8n_rag_1_docs_users
  where metadata @> filter
  order by n8n_rag_1_docs_users.embedding <=> query_embedding
  limit match_count;
end;
$$;
