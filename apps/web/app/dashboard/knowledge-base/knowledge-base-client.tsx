"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { FileText, RefreshCw, Search, Trash2, UploadCloud } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  deleteDocument,
  getDemoWorkspace,
  getDocuments,
  searchKnowledge,
  uploadDocument,
} from "@/lib/api";
import type { KnowledgeDocument, KnowledgeSearchChunk, Workspace } from "@/lib/types";

const statusTone = {
  uploaded: "blue",
  processing: "amber",
  ready: "green",
  failed: "red",
} as const;

export function KnowledgeBaseClient() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [searchResults, setSearchResults] = useState<KnowledgeSearchChunk[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const readyDocuments = useMemo(
    () => documents.filter((document) => document.status === "ready").length,
    [documents]
  );

  async function loadDocuments() {
    setError(null);
    setIsLoading(true);
    try {
      const demoWorkspace = await getDemoWorkspace();
      setWorkspace(demoWorkspace);
      setDocuments(await getDocuments(demoWorkspace.id));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load documents");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!workspace || !selectedFile) {
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    if (title.trim()) {
      formData.append("title", title.trim());
    }

    setIsUploading(true);
    setError(null);
    try {
      await uploadDocument(workspace.id, formData);
      setSelectedFile(null);
      setTitle("");
      form.reset();
      setDocuments(await getDocuments(workspace.id));
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(documentId: string) {
    if (!workspace) {
      return;
    }
    setError(null);
    try {
      await deleteDocument(documentId);
      setDocuments(await getDocuments(workspace.id));
      setSearchResults((results) => results.filter((result) => result.document_id !== documentId));
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Delete failed");
    }
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || !query.trim()) {
      return;
    }

    setIsSearching(true);
    setError(null);
    try {
      const response = await searchKnowledge(workspace.id, query.trim(), 5);
      setSearchResults(response.chunks);
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : "Search failed");
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Knowledge Base</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Upload support documents, inspect chunks, and test semantic retrieval.
          </p>
        </div>
        <button
          onClick={() => void loadDocuments()}
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-card px-3 text-sm font-medium"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </section>

      {error ? (
        <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Workspace</p>
          <p className="mt-2 text-lg font-semibold">{workspace?.name ?? "Loading"}</p>
        </article>
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Documents</p>
          <p className="mt-2 text-3xl font-semibold">{documents.length}</p>
        </article>
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Ready for retrieval</p>
          <p className="mt-2 text-3xl font-semibold">{readyDocuments}</p>
        </article>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.78fr_1fr]">
        <form onSubmit={handleUpload} className="rounded-md border border-border bg-card p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <UploadCloud className="h-5 w-5 text-primary" />
            <h3 className="text-base font-semibold">Upload document</h3>
          </div>
          <div className="space-y-4">
            <label className="block">
              <span className="text-sm font-medium">Title</span>
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                placeholder="Refund Policy"
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium">File</span>
              <input
                type="file"
                accept=".pdf,.txt,.md,.markdown"
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                className="mt-2 w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              />
            </label>
            <button
              disabled={!selectedFile || isUploading}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
            >
              <UploadCloud className="h-4 w-4" />
              {isUploading ? "Uploading" : "Upload and process"}
            </button>
          </div>
        </form>

        <form onSubmit={handleSearch} className="rounded-md border border-border bg-card p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <Search className="h-5 w-5 text-primary" />
            <h3 className="text-base font-semibold">Search knowledge</h3>
          </div>
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="h-10 min-w-0 flex-1 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
              placeholder="What is the refund window?"
            />
            <button
              disabled={!query.trim() || isSearching}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Search className="h-4 w-4" />
              Search
            </button>
          </div>
          <div className="mt-5 space-y-3">
            {searchResults.map((result) => (
              <article key={result.chunk_id} className="rounded-md border border-border bg-background p-4">
                <div className="flex items-center justify-between gap-3">
                  <Link
                    href={`/dashboard/knowledge-base/${result.document_id}`}
                    className="text-sm font-semibold text-primary"
                  >
                    {result.document_title}
                  </Link>
                  <Badge tone="blue">{result.score.toFixed(3)}</Badge>
                </div>
                <p className="mt-2 line-clamp-4 text-sm leading-6 text-muted-foreground">
                  {result.content}
                </p>
              </article>
            ))}
            {!searchResults.length ? (
              <p className="rounded-md bg-muted px-3 py-3 text-sm text-muted-foreground">
                Search results will appear here after documents are uploaded.
              </p>
            ) : null}
          </div>
        </form>
      </section>

      <section className="rounded-md border border-border bg-card shadow-sm">
        <div className="border-b border-border px-5 py-4">
          <h3 className="text-base font-semibold">Documents</h3>
        </div>
        {isLoading ? (
          <p className="px-5 py-6 text-sm text-muted-foreground">Loading documents</p>
        ) : documents.length ? (
          <div className="divide-y divide-border">
            {documents.map((document) => (
              <div key={document.id} className="flex flex-wrap items-center justify-between gap-4 px-5 py-4">
                <div className="flex min-w-0 items-center gap-3">
                  <FileText className="h-5 w-5 shrink-0 text-primary" />
                  <div className="min-w-0">
                    <Link
                      href={`/dashboard/knowledge-base/${document.id}`}
                      className="block truncate text-sm font-semibold hover:text-primary"
                    >
                      {document.title}
                    </Link>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {document.filename} · {document.file_type}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge tone={statusTone[document.status]}>{document.status}</Badge>
                  <button
                    onClick={() => void handleDelete(document.id)}
                    className="flex h-9 w-9 items-center justify-center rounded-md border border-border bg-background text-muted-foreground hover:text-rose-700"
                    aria-label={`Delete ${document.title}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="px-5 py-6 text-sm text-muted-foreground">
            No documents yet. Upload a PDF, TXT, or Markdown file to start retrieval.
          </p>
        )}
      </section>
    </div>
  );
}
