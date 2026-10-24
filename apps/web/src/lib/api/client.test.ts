import { describe, expect, it } from "vitest";
import { createApiClient } from "./client";

describe("createApiClient", () => {
  it("initializes an openapi-fetch client with default options", () => {
    const client = createApiClient();
    expect(client).toBeDefined();
    expect(typeof client.GET).toBe("function");
  });

  it("accepts custom baseUrl options", () => {
    const client = createApiClient({ baseUrl: "https://api.example.com" });
    expect(client).toBeDefined();
    expect(typeof client.GET).toBe("function");
  });
});
