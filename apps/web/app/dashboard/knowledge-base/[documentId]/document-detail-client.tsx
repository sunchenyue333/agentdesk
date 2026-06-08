"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { getDocumentChunks, getDocumentDetail } from "@/lib/api";
import type { DocumentChunk, KnowledgeDocumentDetail } from "@/lib/types";

export function DocumentDetailClient({ documentId }: { documentId: string }) {
  const [document, setDocument] = useState<KnowledgeDocumentDetail | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDocument() {
      try {
        const [detail, chunkList] = await Promise.all([
          getDocumentDetail(documentId),
          getDocumentChunks(documentId),
        ]);
        setDocument(detail);
        setChunks(chunkList);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load document");
      }
    }

    void loadDocument();
  }, [documentId]);

  if (error) {
    return (
      <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {error}
      </div>
    );
  }

  if (!document) {
    return <p className="text-sm text-muted-foreground">Loading document</p>;
  }

  return (
    <div className="space-y-6">
      <Link
        href="/dashboard/knowledge-base"
        className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to knowledge base
      </Link>

      <section className="rounded-md border border-border bg-card p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex min-w-0 gap-3">
            <FileText className="mt-1 h-5 w-5 shrink-0 text-primary" />
            <div className="min-w-0">
              <h2 className="text-2xl font-semibold">{document.title}</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {document.filename} · {document.file_type}
              </p>
            </div>
          </div>
          <Badge tone={document.status === "ready" ? "green" : "amber"}>{document.status}</Badge>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <div className="rounded-md bg-muted p-3">
            <p className="text-xs text-muted-foreground">Chunks</p>
            <p className="mt-1 text-xl font-semibold">{document.chunk_count}</p>
          </div>
          <div className="rounded-md bg-muted p-3">
            <p className="text-xs text-muted-foreground">Characters</p>
            <p className="mt-1 text-xl font-semibold">{document.raw_text?.length ?? 0}</p>
          </div>
          <div className="rounded-md bg-muted p-3">
            <p className="text-xs text-muted-foreground">Document ID</p>
            <p className="mt-1 truncate text-sm font-medium">{document.id}</p>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h3 className="text-base font-semibold">Chunk preview</h3>
        {chunks.map((chunk) => (
          <article key={chunk.id} className="rounded-md border border-border bg-card p-4 shadow-sm">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <span className="text-sm font-semibold">Chunk {chunk.chunk_index + 1}</span>
              <span className="text-xs text-muted-foreground">
                {chunk.token_count ?? 0} estimated tokens
              </span>
            </div>
            <p className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">{chunk.content}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
