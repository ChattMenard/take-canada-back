import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App.jsx";

vi.mock("./api.js", () => ({
  api: {
    health: vi.fn(() => Promise.resolve({ status: "ok" })),
    stats: vi.fn(() =>
      Promise.resolve({
        evidence_count: 53,
        entity_count: 22,
        relationship_count: 14,
        timeline_count: 11,
        storage_bytes: 0,
      }),
    ),
  },
  isAuthenticated: vi.fn(() => false),
}));

vi.mock("./components/Navigation.jsx", () => ({
  default: ({ activeView }) => <div data-testid="active-view">{activeView}</div>,
}));

vi.mock("./views/Dashboard/index.jsx", () => ({
  default: () => <h1>Executive dashboard</h1>,
}));

describe("App navigation", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/");
    window.scrollTo = vi.fn();
  });

  it("opens on the executive dashboard when no tier hash is present", async () => {
    render(<App />);

    await waitFor(() => expect(screen.getByTestId("active-view").textContent).toBe("dashboard"));
    expect(screen.getByRole("heading", { name: "Executive dashboard" })).toBeTruthy();
  });
});
