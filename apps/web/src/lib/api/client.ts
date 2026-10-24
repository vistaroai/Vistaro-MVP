import createFetchClient, { type Client } from "openapi-fetch";
import type { paths } from "./schema.d.ts";

export type ApiClient = Client<paths>;

export interface CreateApiClientOptions {
  baseUrl?: string;
  getCsrfToken?: () => string | null;
}

/**
 * Create a typed API client backed by openapi-fetch.
 * Includes credentials by default and forwards CSRF / request tracing headers.
 */
export function createApiClient(options: CreateApiClientOptions = {}): ApiClient {
  const baseUrl = options.baseUrl ?? "";

  const client = createFetchClient<paths>({
    baseUrl,
    credentials: "include",
  });

  return client;
}

export const api = createApiClient();
