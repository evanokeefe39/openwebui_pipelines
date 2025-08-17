def generate_sql_script(table_name: str):
    filename = f"init_{table_name}.sql"

    sql = f"""-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your documents
create table {table_name} (
  id bigserial primary key,
  content text, -- corresponds to Document.pageContent
  metadata jsonb, -- corresponds to Document.metadata
  embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
);

-- Create a function to search for documents
create or replace function match_docs_{table_name} (
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{{}}'
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
    1 - ({table_name}.embedding <=> query_embedding) as similarity
  from {table_name}
  where metadata @> filter
  order by {table_name}.embedding <=> query_embedding
  limit match_count;
end;
$$;
"""
    with open(filename, "w") as f:
        f.write(sql)
    print(f"SQL script written to {filename}")

# Example usage
if __name__ == "__main__":
    generate_sql_script("n8n_rag_1_docs_users")
    generate_sql_script("n8n_rag_1_docs_eval")
